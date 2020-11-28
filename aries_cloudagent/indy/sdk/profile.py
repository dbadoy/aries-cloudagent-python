"""Manage Indy-SDK profile interaction."""

from ...config.provider import ClassProvider
from ...core.profile import Profile, ProfileSession
from ...storage.base import BaseStorage
from ...wallet.base import BaseWallet

from ..holder import IndyHolder
from ..issuer import IndyIssuer
from ..verifier import IndyVerifier

from .wallet_setup import IndyOpenWallet


class IndySdkProfile(Profile):
    """Provide access to Indy profile interaction methods."""

    BACKEND_NAME = "indy"

    def __init__(self, wallet: IndyOpenWallet):
        """Create a new IndyProfile instance."""
        self.wallet = wallet

    @property
    def backend(self) -> str:
        """Accessor for the backend implementation name."""
        return "indy"

    @property
    def name(self) -> str:
        """Accessor for the profile name."""
        return self.wallet.name

    def session(self) -> "ProfileSession":
        """Start a new interactive session with no transaction support requested."""
        return IndySdkProfileSession(self)

    def transaction(self) -> "ProfileSession":
        """
        Start a new interactive session with commit and rollback support.

        If the current backend does not support transactions, then commit
        and rollback operations of the session will not have any effect.
        """
        return IndySdkProfileSession(self)


class IndySdkProfileSession(ProfileSession):
    """An active connection to the profile management backend."""

    def __init__(self, profile: IndySdkProfile):
        """Create a new IndySdkProfileSession instance."""
        super().__init__(profile=profile)

    def _setup(self):
        """Create the session or transaction connection, if needed."""
        super()._setup()
        injector = self._context.injector
        injector.bind_provider(
            BaseStorage,
            ClassProvider("aries_cloudagent.storage.indy.IndyStorage", self.wallet),
        )
        injector.bind_provider(
            BaseWallet,
            ClassProvider("aries_cloudagent.wallet.indy.IndyWallet", self.wallet),
        )
        injector.bind_provider(
            IndyHolder,
            ClassProvider(
                "aries_cloudagent.indy.sdk.holder.IndySdkHolder", self.wallet
            ),
        )
        injector.bind_provider(
            IndyIssuer,
            ClassProvider(
                "aries_cloudagent.indy.sdk.issuer.IndySdkIssuer", self.wallet
            ),
        )
        injector.bind_provider(
            IndyVerifier,
            ClassProvider(
                "aries_cloudagent.indy.sdk.verifier.IndySdkVerifier", self.wallet
            ),
        )
