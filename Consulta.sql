#usuários

SELECT DISTINCT u.gender, u.birthdate, ua.estado, ua.cidade, ua.bairro, up.valid_until, uf.permission, uhp.weight, uhp.height
FROM users u 
LEFT JOIN user_addresses ua ON ua.user_id = u.id 
LEFT JOIN user_plans up ON up.user_id = u.id
LEFT JOIN user_families uf ON uf.user_id = u.id
LEFT JOIN user_health_profiles uhp ON uhp.user_id = u.id


#pagamentos



#agendamentos




#outros