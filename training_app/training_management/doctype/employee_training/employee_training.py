import logging

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, validate_email_address


def get_logger():
    """Writes to sites/<site>/logs/employee_training.log"""
    logger = frappe.logger("employee_training", allow_site=True, file_count=5)
    logger.setLevel(logging.DEBUG)  # default is WARNING, so info/debug would be dropped
    return logger


class EmployeeTraining(Document):
    def validate(self):
        logger = get_logger()
        logger.info(f"[validate] Employee Training {self.name or 'NEW'} for {self.employee_id}")
        try:
            self.validate_duration()
            self.validate_email()
            self.validate_certification()
        except frappe.ValidationError as e:
            logger.error(f"[validate] FAILED for {self.employee_id}: {e}")
            raise

    def validate_duration(self):
        if flt(self.duration_hours) <= 0:
            get_logger().warning(
                f"[validate_duration] Invalid duration {self.duration_hours} for {self.employee_id}"
            )
            frappe.throw(_("Duration (Hours) must be greater than 0"))

    def validate_email(self):
        if not self.employee_email:
            return

        # throw=False returns "" for an invalid address instead of raising
        valid = validate_email_address(self.employee_email, throw=False)

        if not valid:
            get_logger().warning(
                f"[validate_email] Invalid email '{self.employee_email}' "
                f"for employee {self.employee_id} ({self.employee_name})"
            )
            frappe.throw(
                _("{0} is not a valid Email Address").format(self.employee_email),
                title=_("Invalid Email"),
            )

        get_logger().info(f"[validate_email] Email OK for {self.employee_id}")

    def validate_certification(self):
        if self.is_certified and self.status != "Completed":
            get_logger().warning(
                f"[validate_certification] Certified but status={self.status} for {self.employee_id}"
            )
            frappe.throw(_("Only Completed trainings can be marked as certified"))

    def before_save(self):
        get_logger().debug(f"[before_save] {self.name} status={self.status}")

    def after_insert(self):
        get_logger().info(
            f"[after_insert] Created {self.name}: {self.training_name} for {self.employee_name}"
        )

    def on_update(self):
        logger = get_logger()
        logger.info(f"[on_update] Updated {self.name}, status={self.status}")
        if self.status == "Completed":
            logger.info(
                f"[on_update] Training {self.name} COMPLETED, certified={self.is_certified}"
            )

    def on_trash(self):
        get_logger().info(f"[on_trash] Deleting {self.name}")


@frappe.whitelist()
def get_training_records(status=None, limit=20):
    """Custom whitelisted API to fetch training records."""
    logger = get_logger()
    try:
        filters = {"status": status} if status else {}
        data = frappe.get_list(
            "Employee Training",
            filters=filters,
            fields=[
                "name", "employee_id", "employee_name", "training_name",
                "training_type", "training_date", "status", "is_certified",
            ],
            order_by="training_date desc",
            limit_page_length=int(limit),
        )
        logger.info(f"[get_training_records] Fetched {len(data)} records (status={status})")
        return data
    except Exception:
        logger.error(f"[get_training_records] failed: {frappe.get_traceback()}")
        frappe.log_error(title="Employee Training fetch failed", message=frappe.get_traceback())
        raise