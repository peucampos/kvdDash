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
SELECT ues.scheduled data_agendamento, u.id user_id, u.name user_name, u.gender, p.name provider, pu.name provider_unit, pu.bairro,
ues.categoria, uess.status, ues.realizador_nome profissional, ues.procedimento_especialidade_nome
FROM user_exam_schedules ues
JOIN providers p ON p.id = ues.provider_id
JOIN provider_units pu ON pu.id = ues.provider_unit_id
JOIN users u ON u.id = ues.user_id
JOIN user_exam_schedule_statuses uess ON uess.id = ues.status_id
ORDER BY 1 DESC


#afiliados
SELECT ai.user_id id_afiliado, u.name afiliado, ai.commission, ai.payed_at, ai.type, ai.price, ai.discount, uba.pix_type, uba.pix_key
FROM affiliate_invitations ai
JOIN users u ON u.id = ai.user_id
LEFT JOIN user_bank_accounts uba ON uba.user_id = u.id
WHERE ai.payed_at IS NOT NULL AND ai.deleted_at IS NULL
AND ai.price IS NOT NULL AND ai.type IS NOT NULL
AND canceled_at IS NULL AND ai.chargebacked_at IS null


#Consulta Não Renovaram
SELECT u.cpf, u.name, u.phone, u.email, up.valid_until FROM user_plans up
JOIN users u ON u.id = up.user_id
WHERE up.valid_until < CURDATE()
AND YEAR(up.valid_until) = 2024
AND MONTH(up.valid_until) IN (7,8)
AND u.deleted_at IS NULL
AND cpf IS NOT NULL
AND email IS NOT NULL

ORDER BY up.valid_until