from django.core.management.base import BaseCommand
from faker import Faker
from core.models import RestricaoAlimentar


class Command(BaseCommand):
    help = 'Popula o banco de dados com restrições alimentares padrão'

    def handle(self, *args, **options):
        fake = Faker('pt_BR')
        
        restricoes_data = [
            {'tipo': 'Vegetariano', 'descricao': 'Não consome carne vermelha, frango ou peixe'},
            {'tipo': 'Vegano', 'descricao': 'Não consome nenhum produto de origem animal'},
            {'tipo': 'Sem Glúten', 'descricao': 'Intolerância ou alergia ao glúten'},
            {'tipo': 'Sem Lactose', 'descricao': 'Intolerância ou alergia a produtos lácteos'},
            {'tipo': 'Sem Ovo', 'descricao': 'Alergia ou restrição a ovos e derivados'},
            {'tipo': 'Sem Amendoim', 'descricao': 'Alergia a amendoim e derivados'},
            {'tipo': 'Sem Frutos do Mar', 'descricao': 'Alergia ou restrição a frutos do mar'},
            {'tipo': 'Sem Nozes', 'descricao': 'Alergia a nozes e castanhas'},
            {'tipo': 'Keto', 'descricao': 'Dieta cetogênica com restrição de carboidratos'},
            {'tipo': 'Low Carb', 'descricao': 'Restrição de carboidratos'},
            {'tipo': 'Paleo', 'descricao': 'Dieta baseada em alimentos naturais e não processados'},
            {'tipo': 'Sem Soja', 'descricao': 'Alergia ou restrição a soja e derivados'},
        ]
        
        created_count = 0
        for restricao_data in restricoes_data:
            restricao, created = RestricaoAlimentar.objects.get_or_create(
                tipo=restricao_data['tipo'],
                defaults={'descricao': restricao_data['descricao'], 'is_active': True}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Criada restrição: {restricao.tipo}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Restrição já existe: {restricao.tipo}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Total de {created_count} novas restrições criadas!')
        )
