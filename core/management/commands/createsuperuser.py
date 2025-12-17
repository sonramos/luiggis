"""
Comando customizado para criar superuser com perfil obrigatório.
"""
from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from core.models import Perfil


class Command(BaseCommand):
    """Cria superuser pedindo também o Perfil."""

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--perfil', type=int, help='ID do Perfil (1=Profissional, 2=Usuário)')

    def handle(self, *args, **options):
        # Obter perfis disponíveis
        perfis = list(Perfil.objects.all().values('id', 'tipo'))
        
        if not perfis:
            self.stdout.write(
                self.style.ERROR(
                    'Erro: Nenhum Perfil disponível. Crie os perfis primeiro via admin ou shell.'
                )
            )
            return

        # Exibir opções de perfil
        self.stdout.write('\nPerfis disponíveis:')
        for perfil in perfis:
            self.stdout.write(f"  {perfil['id']}: {perfil['tipo']}")

        # Obter ID do perfil
        if options.get('perfil'):
            perfil_id = options['perfil']
        else:
            try:
                perfil_id = int(input('Escolha o ID do Perfil: '))
            except ValueError:
                self.stdout.write(self.style.ERROR('ID inválido!'))
                return

        # Validar perfil
        try:
            perfil = Perfil.objects.get(id=perfil_id)
        except Perfil.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Perfil com ID {perfil_id} não existe!'))
            return

        # Armazenar perfil nas opções para usar no método parent
        options['perfil_id'] = perfil_id

        # Chamar método parent para criar superuser
        super().handle(*args, **options)

    def handle_default_username(self, username_field_name, value):
        """Estende para adicionar o perfil após criar o superuser."""
        user = super().handle_default_username(username_field_name, value)
        
        # Adicionar perfil ao usuário recém-criado
        if hasattr(self, '_perfil_id'):
            user.perfil_id = self._perfil_id
            user.save()
        
        return user

    def execute(self, *args, **options):
        """Sobrescreve execute para salvar o perfil_id."""
        if 'perfil_id' in options:
            self._perfil_id = options['perfil_id']
        return super().execute(*args, **options)
