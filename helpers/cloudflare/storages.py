from storages.backends.s3 import S3Storage

class StaticStorage(S3Storage):
    # helpers.cloudflare.storages.StaticStorage
    location = "static"

class MediaStorage(S3Storage):
    # helpers.cloudflare.storages.MediaStorage
    location = "media"

class ProtectedStorage(S3Storage):
    # helpers.cloudflare.storages.MediaStorage
    location = "protected"