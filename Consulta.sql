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


#agendamentos
SELECT ues.scheduled data_agendamento, u.id user_id, u.name user_name, p.name provider, pu.name provider_unit, pu.bairro,
ues.categoria, uess.status
FROM user_exam_schedules ues
JOIN providers p ON p.id = ues.provider_id
JOIN provider_units pu ON pu.id = ues.provider_unit_id
JOIN users u ON u.id = ues.user_id
JOIN user_exam_schedule_statuses uess ON uess.id = ues.status_id
ORDER BY 1 DESC


#outros
Consulta Não Renovaram
SELECT u.cpf, u.name, u.phone, u.email, up.valid_until FROM user_plans up
JOIN users u ON u.id = up.user_id
WHERE up.valid_until < CURDATE()
AND YEAR(up.valid_until) = 2024
AND MONTH(up.valid_until) IN (1,2,3)
AND u.deleted_at IS NULL
AND cpf IS NOT NULL
AND email IS NOT null
ORDER BY up.valid_until