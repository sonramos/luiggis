-- 1. Inserção de Categorias (Garante que existam antes dos ingredientes)
INSERT INTO public.core_categoria (nome, descricao) VALUES
('Proteínas', 'Carnes, ovos e leguminosas ricas em proteína'),
('Vegetais', 'Legumes e verduras frescos'),
('Frutas', 'Frutas frescas e secas'),
('Grãos e Cereais', 'Arroz, massas, aveia e grãos em geral'),
('Laticínios', 'Leite, queijos e derivados'),
('Temperos e Especiarias', 'Ervas e condimentos para sabor'),
('Gorduras e Óleos', 'Azeites, óleos e sementes oleaginosas')
ON CONFLICT (nome) DO NOTHING;

-- 2. Inserção de 50 Ingredientes Variados
-- O campo categoria_id busca o ID dinamicamente pelo nome da categoria
INSERT INTO public.core_ingrediente (nome, caloria, categoria_id) VALUES
-- Proteínas
('Carne Bovina (Patinho)', 250, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Salmão', 208, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Ovo de Galinha', 155, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Grão-de-bico', 164, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Tofu', 76, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Lombo Suíno', 242, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Camarão', 99, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Lentilha', 116, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Tilápia', 128, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Atum em Conserva', 116, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),

-- Vegetais
('Brócolis', 34, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Espinafre', 23, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Cenoura', 41, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Abóbora Cabotiá', 26, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Berinjela', 25, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Couve-flor', 25, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Batata Doce', 86, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Pepino', 15, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Pimentão Amarelo', 20, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Cebola Roxa', 40, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Alho', 149, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Abobrinha', 17, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Aspargos', 20, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Cogumelo Paris', 22, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),

-- Frutas
('Banana Prata', 89, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Maçã Fuji', 52, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Abacate', 160, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Morango', 32, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Manga Palmer', 60, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Laranja Pera', 47, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Limão Siciliano', 29, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Abacaxi', 50, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Uva Passa', 299, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),

-- Grãos e Cereais
('Arroz Integral', 111, (SELECT id FROM core_categoria WHERE nome = 'Grãos e Cereais')),
('Quinoa', 120, (SELECT id FROM core_categoria WHERE nome = 'Grãos e Cereais')),
('Aveia em Flocos', 389, (SELECT id FROM core_categoria WHERE nome = 'Grãos e Cereais')),
('Macarrão Integral', 124, (SELECT id FROM core_categoria WHERE nome = 'Grãos e Cereais')),
('Milho Verde', 86, (SELECT id FROM core_categoria WHERE nome = 'Grãos e Cereais')),
('Feijão Preto', 132, (SELECT id FROM core_categoria WHERE nome = 'Grãos e Cereais')),
('Cuscuz Marroquino', 112, (SELECT id FROM core_categoria WHERE nome = 'Grãos e Cereais')),

-- Laticínios
('Queijo Muçarela', 300, (SELECT id FROM core_categoria WHERE nome = 'Laticínios')),
('Iogurte Natural', 59, (SELECT id FROM core_categoria WHERE nome = 'Laticínios')),
('Leite Desnatado', 35, (SELECT id FROM core_categoria WHERE nome = 'Laticínios')),
('Queijo Cottage', 98, (SELECT id FROM core_categoria WHERE nome = 'Laticínios')),
('Manteiga Ghee', 800, (SELECT id FROM core_categoria WHERE nome = 'Laticínios')),

-- Gorduras, Temperos e Outros
('Azeite de Oliva Extra Virgem', 884, (SELECT id FROM core_categoria WHERE nome = 'Gorduras e Óleos')),
('Castanha-do-Pará', 656, (SELECT id FROM core_categoria WHERE nome = 'Gorduras e Óleos')),
('Mel de Abelha', 304, (SELECT id FROM core_categoria WHERE nome = 'Temperos e Especiarias')),
('Manjericão Fresco', 23, (SELECT id FROM core_categoria WHERE nome = 'Temperos e Especiarias')),
('Alecrim', 131, (SELECT id FROM core_categoria WHERE nome = 'Temperos e Especiarias'))

-- Mais 50 ingredientes
('Carne Moída (Acém)', 212, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Peito de Peru Defumado', 104, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Sardinha em lata', 208, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Proteína de Soja Texturizada', 345, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Feijão Branco', 139, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Feijão Carioca', 76, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Ervilha Fresca', 81, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Carne de Sol', 215, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Bacon em Cubos', 541, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),
('Linguiça Artesanal', 300, (SELECT id FROM core_categoria WHERE nome = 'Proteínas')),

-- Vegetais (Mais cores e texturas)
('Alho-poró', 61, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Beterraba', 43, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Chuchu', 19, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Quiabo', 33, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Rabanete', 16, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Repolho Roxo', 31, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Rúcula', 25, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Salsa (Salsinha)', 36, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Cebolinha Fresca', 30, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Vagem', 31, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Inhame', 118, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Mandioca (Aipim)', 160, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Milho em Espiga', 108, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Couve Manteiga', 27, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),
('Acelga', 19, (SELECT id FROM core_categoria WHERE nome = 'Vegetais')),

-- Frutas (Mais diversidade)
('Maçã Verde', 52, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Pera', 57, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Melancia', 30, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Melão', 34, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Kiwi', 61, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Maracujá', 97, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Goiaba Vermelha', 68, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Tangerina (Mexerica)', 53, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),
('Mamão Papaya', 43, (SELECT id FROM core_categoria WHERE nome = 'Frutas')),

-- Grãos, Cereais e Farinhas
('Granola sem açúcar', 450, (SELECT id FROM core_categoria WHERE nome = 'Grãos e Cereais')),
('Farinha de Trigo Integral', 340, (SELECT id FROM core_categoria WHERE nome = 'Grãos e Cereais')),
('Goma de Tapioca', 240, (SELECT id FROM core_categoria WHERE nome = 'Grãos e Cereais')),
('Macarrão de Arroz (Bifum)', 350, (SELECT id FROM core_categoria WHERE nome = 'Grãos e Cereais')),
('Farelo de Aveia', 246, (SELECT id FROM core_categoria WHERE nome = 'Grãos e Cereais')),
('Farinha de Mandioca', 340, (SELECT id FROM core_categoria WHERE nome = 'Grãos e Cereais')),

-- Laticínios e Substitutos
('Queijo Minas Frescal', 243, (SELECT id FROM core_categoria WHERE nome = 'Laticínios')),
('Ricota', 174, (SELECT id FROM core_categoria WHERE nome = 'Laticínios')),
('Requeijão Cremoso', 257, (SELECT id FROM core_categoria WHERE nome = 'Laticínios')),
('Leite de Amêndoas', 15, (SELECT id FROM core_categoria WHERE nome = 'Laticínios')),
('Kefir de Leite', 60, (SELECT id FROM core_categoria WHERE nome = 'Laticínios')),

-- Temperos e Gorduras
('Orégano Seco', 265, (SELECT id FROM core_categoria WHERE nome = 'Temperos e Especiarias')),
('Páprica Defumada', 282, (SELECT id FROM core_categoria WHERE nome = 'Temperos e Especiarias')),
('Cominho em pó', 375, (SELECT id FROM core_categoria WHERE nome = 'Temperos e Especiarias')),
('Óleo de Coco', 862, (SELECT id FROM core_categoria WHERE nome = 'Gorduras e Óleos')),
('Amêndoas Laminadas', 579, (SELECT id FROM core_categoria WHERE nome = 'Gorduras e Óleos')),
('Noz-moscada', 525, (SELECT id FROM core_categoria WHERE nome = 'Temperos e Especiarias'))
