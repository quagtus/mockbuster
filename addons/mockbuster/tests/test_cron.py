from odoo.tests import tagged

from .common import MockbusterCase


@tagged("post_install", "-at_install", "mockbuster")
class TestOverdueCron(MockbusterCase):
    def _mails_for(self, rentals):
        return self.env["mail.mail"].search(
            [
                ("model", "=", "mockbuster.rental"),
                ("res_id", "in", rentals.ids),
            ]
        )

    def test_reminder_only_for_overdue(self):
        late = self.rent(self.dvd1, days_ago=10)
        on_time = self.rent(self.dvd2)

        self.Rental._cron_send_overdue_reminders()

        mails = self._mails_for(late | on_time)
        self.assertEqual(len(mails), 1)
        self.assertEqual(mails.res_id, late.id)
        self.assertIn(self.customer, mails.recipient_ids)
        self.assertIn("Test Movie", mails.subject)
        self.assertTrue(late.reminder_sent)
        self.assertFalse(on_time.reminder_sent)

    def test_reminder_is_sent_once(self):
        late = self.rent(self.dvd1, days_ago=10)
        self.Rental._cron_send_overdue_reminders()
        self.Rental._cron_send_overdue_reminders()
        self.assertEqual(len(self._mails_for(late)), 1)

    def test_returned_rental_gets_no_reminder(self):
        late = self.rent(self.dvd1, days_ago=10)
        late.action_return()
        self.Rental._cron_send_overdue_reminders()
        self.assertFalse(self._mails_for(late))
