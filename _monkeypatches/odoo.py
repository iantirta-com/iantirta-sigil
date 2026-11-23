
import os
from pathlib import Path

import odoo
import odoo.release
import odoo.tools.convert as convert
from lxml import etree


def patch_etree_parse_rng():
    custom_rng = Path(__file__).with_name("import_xml.rng").resolve()
    orig_rng = os.path.join(odoo.tools.config.root_path, "import_xml.rng")

    orig_parse = etree.parse
    def patch_etree_parse(schema, *args, **kwargs):
        if schema == orig_rng:
            return orig_parse(custom_rng.as_posix())
        return orig_parse(schema)

    etree.parse = patch_etree_parse


def patch_module():
    odoo.release.author = "iantirta.com"
    # odoo.release.author_email = 'info@iantirta.com'
    convert.xml_import.DATA_ROOTS.append("sigil")
    patch_etree_parse_rng()
