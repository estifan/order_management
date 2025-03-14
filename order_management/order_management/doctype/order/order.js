// Copyright (c) 2025, Tilet Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Order', {
	services_add: function(frm) {
        calculateTotals(frm);
    },

	advance_payment: function(frm) {
        if (frm.doc.full_payment && frm.doc.advance_payment) {
            frm.set_value('remaining_payment', frm.doc.full_payment - frm.doc.advance_payment);
        } else {
            frm.set_value('remaining_payment', frm.doc.full_payment || 0);
        }
    },

	full_payment: function(frm) {
        if (frm.doc.full_payment && frm.doc.advance_payment) {
            frm.set_value('remaining_payment', frm.doc.full_payment - frm.doc.advance_payment);
        } else {
            frm.set_value('remaining_payment', frm.doc.full_payment || 0);
        }
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
    },
	unit_price: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let total_price = row.quantity * row.unit_price;
        frappe.model.set_value(cdt, cdn, 'total_price', total_price);
    },

});

function calculateTotals(frm) {
    // let total_qty = 0;
    let total_order_price = 0;
    frm.doc.services.forEach(function(item) {
        // total_qty += item.qty;
        total_order_price += item.total_price;
    });
    // frm.set_value('total_quantity', total_qty);
    frm.set_value('full_payment', total_order_price);
}