import docutils.core

docutils.core.publish_file(
    source_path="docs/index.rst",
    destination_path="docs/index.html",
    writer_name="html"
)