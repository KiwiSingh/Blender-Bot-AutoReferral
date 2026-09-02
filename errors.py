class BlenderReferralError(Exception):
    """Base exception for the Blender referral automation project."""
    pass


class BlenderResponseError(BlenderReferralError):
    """Raised when Blender fails to provide a usable response."""
    pass


class BlenderResponseTimeoutError(BlenderResponseError):
    """Raised when Blender does not respond within the expected time."""
    pass


class ResponseRetrievalError(BlenderReferralError):
    """Raised when the response from Blender bot cannot be retrieved."""
    pass


class WhatsAppError(BlenderReferralError):
    """Base exception for WhatsApp-related failures."""
    pass


class UnknownUserError(WhatsAppError):
    """Raised when a phone number is not registered on WhatsApp."""
    pass


class ChatOpenError(WhatsAppError):
    """Raised when a WhatsApp chat cannot be opened."""
    pass


class MessageSendError(WhatsAppError):
    """Raised when a text message cannot be sent."""
    pass


class ResumeUploadError(WhatsAppError):
    """Raised when the resume cannot be uploaded or sent."""
    pass