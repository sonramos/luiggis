"""
Comando para popular o banco de dados com receitas fake usando Faker.
"""
from django.core.management.base import BaseCommand
from faker import Faker
import random
from core.models import Receita, Usuario, Ingrediente, IngredienteReceita


class Command(BaseCommand):
    help = 'Cria 20 receitas fake usando Faker'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quantidade',
            type=int,
            default=20,
            help='Quantidade de receitas a serem criadas (padrão: 20)'
        )

    def handle(self, *args, **options):
        fake = Faker('pt_BR')
        quantidade = options['quantidade']
        
        # Verificar se há usuários no sistema
        usuarios = list(Usuario.objects.all())
        if not usuarios:
            self.stdout.write(
                self.style.ERROR('Nenhum usuário encontrado. Crie um superuser primeiro.')
            )
            return
        
        # Verificar se há ingredientes
        ingredientes = list(Ingrediente.objects.all())
        if not ingredientes:
            self.stdout.write(
                self.style.WARNING('Nenhum ingrediente encontrado. Criando alguns ingredientes básicos...')
            )
            self._criar_ingredientes_basicos()
            ingredientes = list(Ingrediente.objects.all())
        
        self.stdout.write(f'Criando {quantidade} receitas fake...')
        
        tipos_receita = [
            'Bolo de', 'Torta de', 'Sopa de', 'Salada de', 'Risoto de',
            'Frango com', 'Carne com', 'Peixe com', 'Macarrão com',
            'Pizza de', 'Panqueca de', 'Lasanha de', 'Gratinado de'
        ]
        
        complementos = [
            'chocolate', 'morango', 'limão', 'laranja', 'cenoura',
            'queijo', 'presunto', 'frango', 'legumes', 'carne',
            'cogumelos', 'camarão', 'atum', 'tomate', 'espinafre'
        ]
        
        receitas_criadas = 0
        
        for _ in range(quantidade):
            try:
                # Gerar título da receita
                tipo = random.choice(tipos_receita)
                complemento = random.choice(complementos)
                titulo = f'{tipo} {complemento}'.title()
                
                # Gerar instruções
                num_passos = random.randint(4, 8)
                passos = []
                for i in range(1, num_passos + 1):
                    passo = fake.sentence(nb_words=random.randint(8, 15))
                    passos.append(f'{i}. {passo}')
                instrucoes = '\n'.join(passos)
                
                # Dados da receita
                tempo_preparo = random.randint(15, 120)
                is_ai_generated = random.choice([True, False])
                owner = random.choice(usuarios)
                
                # Criar receita
                receita = Receita.objects.create(
                    titulo=titulo,
                    instrucoes=instrucoes,
                    tempo_preparo=tempo_preparo,
                    is_ai_generated=is_ai_generated,
                    owner=owner,
                    prompt_geracao=fake.text(max_nb_chars=200) if is_ai_generated else ''
                )
                
                # Adicionar ingredientes aleatórios (entre 3 e 8)
                num_ingredientes = random.randint(3, min(8, len(ingredientes)))
                ingredientes_selecionados = random.sample(ingredientes, num_ingredientes)
                
                for ingrediente in ingredientes_selecionados:
                    IngredienteReceita.objects.create(
                        receita=receita,
                        ingrediente=ingrediente
                    )
                
                receitas_criadas += 1
                self.stdout.write('.', ending='')
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'\nErro ao criar receita: {e}')
                )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ {receitas_criadas} receitas criadas com sucesso!'
            )
        )
    
    def _criar_ingredientes_basicos(self):
        """Cria alguns ingredientes básicos se não existirem."""
        from core.models import Categoria
        
        # Criar categorias se não existirem
        cat_legumes, _ = Categoria.objects.get_or_create(
            nome='Legumes',
            defaults={'descricao': 'Vegetais e legumes'}
        )
        cat_carnes, _ = Categoria.objects.get_or_create(
            nome='Carnes',
            defaults={'descricao': 'Carnes e proteínas'}
        )
        cat_laticinios, _ = Categoria.objects.get_or_create(
            nome='Laticínios',
            defaults={'descricao': 'Leite, queijos e derivados'}
        )
        cat_graos, _ = Categoria.objects.get_or_create(
            nome='Grãos',
            defaults={'descricao': 'Arroz, feijão, massas'}
        )
        
        ingredientes_basicos = [
            ('Tomate', cat_legumes, 20),
            ('Cebola', cat_legumes, 40),
            ('Alho', cat_legumes, 150),
            ('Cenoura', cat_legumes, 35),
            ('Batata', cat_legumes, 80),
            ('Frango', cat_carnes, 165),
            ('Carne Bovina', cat_carnes, 250),
            ('Peixe', cat_carnes, 120),
            ('Queijo', cat_laticinios, 350),
            ('Leite', cat_laticinios, 60),
            ('Arroz', cat_graos, 130),
            ('Macarrão', cat_graos, 150),
            ('Feijão', cat_graos, 120),
        ]
        
        for nome, categoria, caloria in ingredientes_basicos:
            Ingrediente.objects.get_or_create(
                nome=nome,
                defaults={
                    'categoria': categoria,
                    'caloria': caloria
                }
            )
        
        self.stdout.write(
            self.style.SUCCESS('✅ Ingredientes básicos criados!')
        )
