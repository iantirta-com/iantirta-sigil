import re

from odoo import _, fields, models

URL_SPLIT_RE = re.compile(r"[,;\s]+")


class KaraokeBatchInputWizard(models.TransientModel):
    _name = 'karaoke.batch.input.wizard'
    _description = 'Karaoke Batch Input'

    youtube_urls = fields.Text("URL'S", required=True, help="split by `,`")
    karaoke_type = fields.Selection([
        ("basic", "Basic"),
        ("plus", "Plus (Lyrics Subtitle)"),
    ], required=True, string="Karaoke Generation Type")

    def action_on_click_create(self):
        self.ensure_one()

        raw_urls = [
            url.strip().rstrip("/")
            for url in URL_SPLIT_RE.split(self.youtube_urls or "")
            if url.strip()
        ]
        inputted_urls = set(raw_urls)

        existing_records = self.env["karaoke.karaoke"].sudo().search_read(
            domain=[("source_url", "in", list(inputted_urls))],
            fields=["source_url"],
        )
        existing_urls = {rec["source_url"] for rec in existing_records}

        to_create = [
            {"source_url": url, "karaoke_type": self.karaoke_type}
            for url in inputted_urls
            if url not in existing_urls
        ]

        created_count = 0
        if to_create:
            karaokes = self.env["karaoke.karaoke"].create(to_create)
            created_count = len(karaokes)

        duplicate_count = len(raw_urls) - created_count

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _(
                "Created %(created)s karaoke task(s). Duplicated: %(dup)s."
                )
                % {"created": created_count, "dup": duplicate_count},
                "type": "success" if created_count else "warning",
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
