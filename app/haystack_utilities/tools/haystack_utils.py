# For file type routing
mime_types = ["application/pdf", r"text/.*", "application/vnd.openxmlformats-officedocument.presentationml.presentation", r"application/x-ipynb\+json"]
additional_mimetypes = {
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "application/x-ipynb+json": ".ipynb"
    }