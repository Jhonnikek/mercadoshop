from core.models import Carrito

def cart_counter(request):
    if request.user.is_authenticated and request.user.tipo_usuario == 'CLIENTE':
        cart = Carrito.objects.filter(cliente=request.user, estado='Activo').first()
        if cart:
            return {'cart_items_count': sum(item.cantidad for item in cart.items.all())}
    return {'cart_items_count': 0}
