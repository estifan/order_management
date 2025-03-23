frappe.ui.form.on('Order', {
    refresh: function(frm) {
        calculate_total_payment(frm);

        frm.fields_dict.services.grid.get_field('designed').get_query = function(doc, cdt, cdn) {
            return {
                query: 'order_management.order_management.doctype.order.user_filter.get_users_by_role',
                filters: {
                    role: 'Designer' 
                }
            };
        };

        frm.fields_dict.services.grid.get_field('workshoped').get_query = function(doc, cdt, cdn) {
            return {
                query: 'order_management.order_management.doctype.order.user_filter.get_users_by_role',
                filters: {
                    role: 'Workshop' 
                }
            };
        };
    
    },

    services_add: function(frm) {
        calculateTotals(frm);
    },

    advance_payment: function(frm) {
        calculateRemainingPayment(frm);
    },

    final_payment: function(frm) {
        calculateRemainingPayment(frm);
    },

    full_payment: function(frm) {
        calculateRemainingPayment(frm);
    },

    before_save: function(frm) {
        let today = new Date();
        let formattedDate = today.toISOString().split('T')[0];
        frappe.model.set_value(frm.doctype, frm.docname, 'ordered_date', formattedDate);
        console.log('Ordered date set to:', formattedDate);
    },
});

frappe.ui.form.on('Service Item', {
    service: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        frappe.model.set_value(cdt, cdn, 'quantity', 1);

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Service',
                filters: { service_name: row.service },
                fields: ['price'],
                limit: 1
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    let unit_price = r.message[0].price;
                    frappe.model.set_value(cdt, cdn, 'unit_price', unit_price);
                    let total_price = row.quantity * unit_price;
                    frappe.model.set_value(cdt, cdn, 'total_price', total_price);
                } else {
                    frappe.model.set_value(cdt, cdn, 'rate', 0);
                    frappe.model.set_value(cdt, cdn, 'total_price', 0);
                }
            }
        });
    },

    quantity: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let total_price = row.quantity * row.unit_price;
        frappe.model.set_value(cdt, cdn, 'total_price', total_price);
    }
});

function calculateTotals(frm) {
    let total_order_price = 0;
    frm.doc.services.forEach(function(item) {
        total_order_price += item.total_price;
    });
    frm.set_value('full_payment', total_order_price);
}

frappe.ui.form.on('Service Item', {
    total_price: function(frm, cdt, cdn) {
        calculate_total_payment(frm);
    },
    services_remove: function(frm) {
        calculate_total_payment(frm);
    }
});

function calculate_total_payment(frm) {
    let total = 0;
    if (frm.doc.services) {
        frm.doc.services.forEach(row => {
            total += row.total_price || 0;
        });
    }
    frm.set_value('full_payment', total);
    calculateRemainingPayment(frm);
}

function calculateRemainingPayment(frm) {
    let full_payment = frm.doc.full_payment || 0;
    let advance_payment = frm.doc.advance_payment || 0;
    let final_payment = frm.doc.final_payment || 0;

    let remaining_payment = full_payment - advance_payment - final_payment;
    frm.set_value('remaining_payment', remaining_payment);
}