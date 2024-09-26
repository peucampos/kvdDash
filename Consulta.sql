#usuários
SELECT DISTINCT u.id, u.name, u.email, u.phone, u.gender, u.birthdate,
ua.estado, ua.cidade, ua.bairro, up.valid_until, uf.permission, uhp.weight, uhp.height
FROM users u 
LEFT JOIN user_addresses ua ON ua.user_id = u.id 
LEFT JOIN user_plans up ON up.user_id = u.id
LEFT JOIN user_families uf ON uf.user_id = u.id
LEFT JOIN user_health_profiles uhp ON uhp.user_id = u.id


#pagamentos
SELECT up.created_at, up.updated_at, u.id user_id, u.name user, ups.slug STATUS, up.payable_type, 
up.pay_type, up.installments, up.price, up.split_value, up.sell_affiliate, up.sell_app, up.sell_landpage, up.sell_klingo
FROM user_payments up
LEFT JOIN users u ON u.id = up.user_id
LEFT JOIN user_payment_statuses ups ON ups.id = up.user_payment_status_id

SELECT * FROM user_payment_statuses
#agendamentos
SELECT * FROM user_exam_schedules



#outros