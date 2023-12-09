from .test_hr_timesheet_sheet import TestHrTimesheetSheet


class TestHrTimesheetReviewerNoEmail(TestHrTimesheetSheet):
    @classmethod
    def setUpClass(cls):
        super(TestHrTimesheetReviewerNoEmail, cls).setUpClass()
        cls.timesheet_model_obj = cls.env["hr_timesheet.sheet"]
        cls.mail_message_obj = cls.env["mail.message"]
        cls.mail_thread_obj = cls.env["mail.thread"]
        cls.message_dict = {
            "subject": "Test Message #1",
            "body": "Test Message Content",
            "model": "hr_timesheet.sheet",
            "message_type": "notification",
        }

    def test_notify_compute_recipients_notif_enable(self):
        """Tests notify compute recipients

        when 'not send email to reviewer' flag is disable
        it's should not prevent sending emails to the reviewer
        """
        timesheet = self.timesheet_model_obj.with_user(self.user_4).create(
            {
                "name": "Test Timesheet",
                "employee_id": self.department_manager.id,  # user_3
            }
        )
        msg_dict = self.message_dict.copy()
        # Message created when creating timesheet
        message_create = self.mail_message_obj.search(
            [("model", "=", "hr_timesheet.sheet"), ("res_id", "=", timesheet.id)]
        )
        # send timesheet to review
        timesheet.with_user(self.user_3).action_timesheet_confirm()
        self.assertEqual(
            timesheet.state, "confirm", msg="Timesheet state must be 'confirm'"
        )
        # find all possible reviewers
        possible_reviewers = timesheet._get_possible_reviewers().mapped("partner_id")
        msg_dict.update(
            author_id=self.user_3.partner_id.id,
            email_from=self.user_3.email,
            res_id=timesheet.id,
            parent_id=message_create.id,
            subtype_id=timesheet._track_subtype(init_values=timesheet).id,
            partner_ids=timesheet.message_follower_ids.partner_id.ids,
        )
        # Create notification message when timesheet confirmed
        self.mail_message_obj.create(msg_dict)
        message_confirm = self.mail_message_obj.search(
            [
                ("model", "=", "hr_timesheet.sheet"),
                ("res_id", "=", timesheet.id),
                ("subtype_id.name", "=", "Waiting Review"),
            ]
        )
        rdata = self.mail_thread_obj._notify_compute_recipients(
            message=message_confirm, msg_vals=msg_dict
        )

        # Call the method being tested
        timesheet._notify_record_by_email(
            message=message_confirm, recipients_data=rdata
        )
        recipient_ids = message_confirm.notification_ids.res_partner_id.ids

        # All Possible reviewers should be in recipients
        self.assertTrue(
            any(reviewer in recipient_ids for reviewer in possible_reviewers.ids),
            msg="All Possible reviewers should be in recipients",
        )

    def test_notify_compute_recipients_notif_disable(self):
        """Tests notify compute recipients

        when 'not send email to reviewer' flag is enable
        it's should prevent sending emails to the reviewer
        """
        timesheet = self.timesheet_model_obj.with_user(self.user_4).create(
            {
                "name": "Test Timesheet",
                "employee_id": self.department_manager.id,  # user_3
            }
        )
        # Enable 'not send email to reviewer' flag
        timesheet.company_id.sudo().write(
            {
                "hr_timesheet_reviewer_no_email": True,
            }
        )
        msg_dict = self.message_dict.copy()

        # find all possible reviewers
        possible_reviewers = timesheet._get_possible_reviewers().mapped("partner_id")

        # Message created when creating timesheet
        message_create = self.mail_message_obj.search(
            [("model", "=", "hr_timesheet.sheet"), ("res_id", "=", timesheet.id)]
        )
        # send timesheet to review
        timesheet.with_user(self.user_3).action_timesheet_confirm()
        self.assertEqual(
            timesheet.state, "confirm", msg="Timesheet state must be 'confirm'"
        )
        msg_dict.update(
            author_id=self.user_3.partner_id.id,
            email_from=self.user_3.email,
            res_id=timesheet.id,
            parent_id=message_create.id,
            subtype_id=timesheet._track_subtype(init_values=timesheet).id,
            partner_ids=timesheet.message_follower_ids.partner_id.ids,
        )
        # Create notification message when timesheet confirmed
        self.mail_message_obj.create(msg_dict)
        message_confirm = self.mail_message_obj.search(
            [
                ("model", "=", "hr_timesheet.sheet"),
                ("res_id", "=", timesheet.id),
                ("subtype_id.name", "=", "Waiting Review"),
            ]
        )
        # Get recipients list
        rdata = self.mail_thread_obj._notify_compute_recipients(
            message=message_confirm, msg_vals=msg_dict
        )

        # Call the method being tested
        timesheet._notify_record_by_email(
            message=message_confirm, recipients_data=rdata
        )
        recipient_ids = message_confirm.notification_ids.res_partner_id.ids

        # create set of recipients id
        recipient_ids = set(recipient_ids)
        # create set of possible reviewers id
        possible_reviewer_ids = set(possible_reviewers.ids)

        self.assertSetEqual(
            possible_reviewer_ids.intersection(recipient_ids),
            set(),
            msg="Possible reviewers must not be in recipients",
        )

        # Change review policy
        timesheet.review_policy = "hr_manager"
        # find all possible reviewers for new review policy
        possible_reviewers = timesheet._get_possible_reviewers().mapped("partner_id")

        # Confirm timesheet
        timesheet.with_user(self.user_4).action_timesheet_done()
        self.assertEqual(timesheet.state, "done", msg="Timesheet state must be 'done'")

        # Create notification message when timesheet approved
        msg_dict.update(
            author_id=self.user_4.partner_id.id,
            email_from=self.user_4.email,
            subtype_id=timesheet._track_subtype(init_values=timesheet).id,
        )
        self.mail_message_obj.create(msg_dict)
        message_done = self.mail_message_obj.search(
            [
                ("model", "=", "hr_timesheet.sheet"),
                ("res_id", "=", timesheet.id),
                ("subtype_id.name", "=", "Approved"),
            ]
        )
        # Get recipients data
        rdata = self.mail_thread_obj._notify_compute_recipients(
            message=message_done, msg_vals=msg_dict
        )

        # Call the method being tested
        timesheet._notify_record_by_email(message=message_done, recipients_data=rdata)
        recipient_ids = message_done.notification_ids.res_partner_id.ids
        partner_follower_ids = timesheet.message_follower_ids.partner_id.ids

        # create set of recipients id
        recipient_ids = set(recipient_ids)
        # create set of possible reviewers id
        possible_reviewer_ids = set(possible_reviewers.ids)
        # create set of followers
        partner_follower_ids = set(partner_follower_ids)
        # create set of followers whose must sended email
        partner_follower_got_email_ids = {
            id
            for id in partner_follower_ids
            if id not in possible_reviewer_ids and id != msg_dict["author_id"]
        }

        self.assertSetEqual(
            possible_reviewer_ids.intersection(recipient_ids),
            set(),
            msg="Possible reviewers must not be in recipients",
        )
        self.assertSetEqual(
            partner_follower_ids.intersection(recipient_ids),
            partner_follower_got_email_ids,
            msg="Followers whose have not right to review must be in recipients",
        )
