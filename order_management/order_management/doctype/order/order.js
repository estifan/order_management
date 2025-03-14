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
	after_save: function(frm) {
        let assigned_users = [];

        if (frm.doc.services) {
            if (Array.isArray(frm.doc.services)) {
                
                let itemCodes = frm.doc.services.map(item => item.service);

                frappe.call({
					method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Service',
                        filters: { service_name: ['in', itemCodes] },
                        fields: ['service_name']
                    },
                    callback: function(menuResults) {
                        if (menuResults.message && menuResults.message.length > 0) {

                            frm.doc.services.forEach(function(item) {
                                if (item.designed || item.workshoped) {
                                    assigned_users.push({
                                        designed: item.designed,
										workshoped: item.workshoped,
                                        service: item.service,
                                        item_name: item.item_name,
                                        qty: item.quantity,
                                        name: item.name,
                                    });
                                }
                            });

                            assigned_users.forEach(function(user) {
                                frappe.call({
                                    method: 'frappe.client.get_list',
                                    args: {
                                        doctype: 'Single Orders',
                                        filters: {
                                            service: user.service,
                                            customer_name: frm.doc.customer_name,
                                            recieved_by: frm.doc.recieved_by,
                                            designed: user.designed,
											workshoped: user.workshoped,
                                            source_docname: user.name
                                        },
                                        fields: ['name']
                                    },
                                    callback: function(r) {
                                        if (r.message.length === 0) {
                                            frappe.call({
                                                method: 'frappe.client.insert',
                                                args: {
                                                    doc: {
                                                        doctype: 'Single Orders',
                                                        service: user.service,
                                                        customer_name: frm.doc.customer_name,
                                                        revieved_by: frm.doc.recieved_by,
														contact_person: frm.doc.contact_person,
                                                        qty: user.qty,
                                                        designed: user.designed,
														workshoped: user.workshoped,
                                                        status: 'Pending',
                                                        source_docname: user.name,
                                                        order_number: frm.doc.name,
                                                    }
                                                },
                                                callback: function(r) {
                                                    if (!r.exc) {
                                                        frappe.show_alert({
                                                            message: __('Single Order created with Service {0} and quantity {1}', [user.service, user.qty]),
                                                            indicator: 'green',
                                                            persist: true
                                                        });

                                                        frappe.call({
                                                            method: 'frappe.share.add',
                                                            args: {
                                                                doctype: 'Single Orders',
                                                                name: r.message.name,
                                                                user: user.designed,
																user: user.workshoped,
                                                                read: 1,
                                                                write: 1,
                                                                share: 0,
                                                                everyone: 0,
                                                                notify: 1
                                                            },
                                                            callback: function(share_res) {
                                                                if (!share_res.exc) {
                                                                    console.log('Shared Single Orders with user:', user.designed);
                                                                } else {
                                                                    frappe.msgprint(__('Error sharing Single Orders '));
                                                                }
                                                            }
                                                        });

                                                    } else {
                                                        frappe.msgprint(__('Error creating Single Order '));
                                                    }
                                                }
                                            });
                                        } else {
                                            console.log('Single Orders already exists for', user.service, 'assigned to', user.designed);
                                        }
                                    }
                                });
                            });
                        } else {
                            console.log('No menu images found');
                        }
                    }
                });
            } else {
                console.log('service_items is not an array, it is a', typeof frm.doc.services);
            }
        } else {
            console.log('service_items field is undefined or null');
        }

        // frappe.realtime.publish('update_single_order', {
        //     'hotel_order_name': frm.doc.name,
        //     'status': frm.doc.status
        // });
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

});

function calculateTotals(frm) {
    let total_order_price = 0;
    frm.doc.services.forEach(function(item) {
        total_order_price += item.total_price;
    });
    frm.set_value('full_payment', total_order_price);
}