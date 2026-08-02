"""
DocuSign e-signature integration point.

IMPORTANT: This is a structured STUB. Real e-signatures require your own
DocuSign developer account, API keys (integration key, user ID, account
ID, and an RSA keypair for JWT auth), which are not available in this
build environment. The functions below show exactly where those
credentials plug in and mirror DocuSign's real eSignature REST API
shape, so wiring in live credentials later is a credentials-and-testing
job, not a redesign.

Docs: https://developers.docusign.com/docs/esign-rest-api/

Until real credentials are added, `send_envelope()` falls back to the
in-app simulated signing used elsewhere in this demo (see db.py's
sign_next_approval), so the rest of the workflow can be built and
demoed end-to-end today.
"""

# --- Real DocuSign wiring goes here once credentials are available ---
DOCUSIGN_INTEGRATION_KEY = None   # from your DocuSign Admin > Apps and Keys
DOCUSIGN_USER_ID = None           # API username (GUID) of the sending account
DOCUSIGN_ACCOUNT_ID = None        # DocuSign account ID
DOCUSIGN_BASE_URL = None          # e.g. https://demo.docusign.net/restapi (sandbox) or production
DOCUSIGN_PRIVATE_KEY_PATH = None  # RSA private key file for JWT grant auth


def is_configured():
    return all([
        DOCUSIGN_INTEGRATION_KEY, DOCUSIGN_USER_ID,
        DOCUSIGN_ACCOUNT_ID, DOCUSIGN_BASE_URL, DOCUSIGN_PRIVATE_KEY_PATH,
    ])


def send_envelope(pdf_path, request, approvers):
    """
    Real implementation (once configured) would:
      1. Authenticate via JWT grant using the private key
      2. Build an EnvelopeDefinition with the PDF as a document
      3. Add one Signer per approver in `approvers`, each with
         routingOrder matching the approval sequence (so DocuSign
         enforces sequential signing exactly like the paper process)
      4. Call envelopes.create() via the DocuSign Python SDK
      5. Store the returned envelope_id against the request so status
         webhooks (Connect) can update approval status automatically

    Example shape (for when credentials are added):

        from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition
        api_client = ApiClient()
        api_client.host = DOCUSIGN_BASE_URL
        api_client.set_default_header("Authorization", f"Bearer {access_token}")
        envelopes_api = EnvelopesApi(api_client)
        envelope_summary = envelopes_api.create_envelope(
            DOCUSIGN_ACCOUNT_ID, envelope_definition=envelope_definition
        )
        return envelope_summary.envelope_id

    For now (no credentials configured), this returns None and the app
    falls back to the in-app simulated approval flow.
    """
    if not is_configured():
        return None
    raise NotImplementedError("Add DocuSign credentials above to enable real e-signature sending.")
