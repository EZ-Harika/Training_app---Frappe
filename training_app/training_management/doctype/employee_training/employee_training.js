frappe.ui.form.on("Employee Training", {
    refresh(frm) {
        frm.add_custom_button(__("View Training Records"), () => {
            frappe.call({
                method: "training_app.training_management.doctype.employee_training.employee_training.get_training_records",
                args: { limit: 20 },
                freeze: true,
                freeze_message: __("Fetching training records..."),
                callback(r) {
                    const rows = r.message || [];
                    if (!rows.length) {
                        frappe.msgprint(__("No training records found"));
                        return;
                    }
                    const esc = frappe.utils.escape_html;
                    const body = rows.map(d => `
                        <tr>
                            <td>${esc(d.name)}</td>
                            <td>${esc(d.employee_id || "")}</td>
                            <td>${esc(d.employee_name || "")}</td>
                            <td>${esc(d.training_name || "")}</td>
                            <td>${esc(d.training_type || "")}</td>
                            <td>${esc(d.training_date || "")}</td>
                            <td>${esc(d.status || "")}</td>
                        </tr>`).join("");

                    const dialog = new frappe.ui.Dialog({
                        title: __("Employee Training Records"),
                        size: "extra-large",
                        fields: [{
                            fieldtype: "HTML",
                            fieldname: "records_html",
                            options: `
                                <table class="table table-bordered">
                                    <thead><tr>
                                        <th>ID</th><th>Emp ID</th><th>Employee</th>
                                        <th>Training</th><th>Type</th><th>Date</th><th>Status</th>
                                    </tr></thead>
                                    <tbody>${body}</tbody>
                                </table>`,
                        }],
                        primary_action_label: __("Close"),
                        primary_action() { dialog.hide(); },
                    });
                    dialog.show();
                },
            });
        });
    },
});