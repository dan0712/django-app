# -*- coding: utf-8 -*-
# author: Glen Baker <iepathos@gmail.com>
from django.core.management import BaseCommand
from django.conf import settings
import logging
import os
from swiftclient.multithreading import OutputManager
from swiftclient.service import SwiftError, SwiftService, SwiftUploadObject

logging.basicConfig(level=logging.ERROR)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("swiftclient").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    # Show this when the user types help
    help = "Upload media files to softlayer cloud."

    # A command must define handle()
    def handle(self, *args, **options):
        _opts = {'object_uu_threads': 20}
        dir = 'media'  # settings.MEDIA_ROOT
        container = settings.SWIFT_CONTAINER_NAME
        with SwiftService(options=_opts) as swift, OutputManager() as out_manager:
            try:
                # Collect all the files and folders in the given directory
                objs = []
                dir_markers = []
                # change to directory so it isn't uploaded as part of all the
                # file object names
                os.chdir(dir)
                for (_dir, _ds, _fs) in os.walk('.'):
                    if not (_ds + _fs):
                        dir_markers.append(_dir)
                    else:
                        objs.extend([os.path.join(_dir, _f) for _f in _fs])

                # Now that we've collected all the required files and dir markers
                # build the ``SwiftUploadObject``s for the call to upload
                objs = [
                    SwiftUploadObject(
                        o, object_name=o.replace(
                            dir, dir, 1
                        )
                    ) for o in objs
                ]
                dir_markers = [
                    SwiftUploadObject(
                        None, object_name=d.replace(
                            dir, dir, 1
                        ), options={'dir_marker': True}
                    ) for d in dir_markers
                ]

                # Schedule uploads on the SwiftService thread pool and iterate
                # over the results
                for r in swift.upload(container, objs + dir_markers):
                    if r['success']:
                        if 'object' in r:
                            print(r['object'])
                        elif 'for_object' in r:
                            print(
                                '%s segment %s' % (r['for_object'],
                                                   r['segment_index'])
                            )
                    else:
                        error = r['error']
                        if r['action'] == "create_container":
                            logger.warning(
                                'Warning: failed to create container '
                                "'%s'%s", container, error
                            )
                        elif r['action'] == "upload_object":
                            logger.error(
                                "Failed to upload object %s to container %s: %s" %
                                (container, r['object'], error)
                            )
                        else:
                            logger.error("%s" % error)
                os.chdir('..')

            except SwiftError as e:
                logger.error(e.value)
