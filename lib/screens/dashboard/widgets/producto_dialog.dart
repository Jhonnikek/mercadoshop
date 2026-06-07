import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../models/producto.dart';

class ProductoDialog extends StatefulWidget {
  final Producto? producto; // null = create mode
  final Future<bool> Function(Producto producto) onSave;

  const ProductoDialog({
    super.key,
    this.producto,
    required this.onSave,
  });

  @override
  State<ProductoDialog> createState() => _ProductoDialogState();
}

class _ProductoDialogState extends State<ProductoDialog> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nombreCtrl;
  late final TextEditingController _precioCtrl;
  late final TextEditingController _stockCtrl;
  late final TextEditingController _descripcionCtrl;
  bool _saving = false;

  bool get _isEditing => widget.producto != null;

  @override
  void initState() {
    super.initState();
    _nombreCtrl = TextEditingController(text: widget.producto?.nombre ?? '');
    _precioCtrl = TextEditingController(
      text: widget.producto != null
          ? widget.producto!.precio.toString()
          : '',
    );
    _stockCtrl = TextEditingController(
      text: widget.producto != null
          ? widget.producto!.stock.toString()
          : '',
    );
    _descripcionCtrl =
        TextEditingController(text: widget.producto?.descripcion ?? '');
  }

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _precioCtrl.dispose();
    _stockCtrl.dispose();
    _descripcionCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);

    final producto = Producto(
      id: widget.producto?.id,
      nombre: _nombreCtrl.text.trim(),
      precio: double.parse(_precioCtrl.text.trim()),
      stock: int.parse(_stockCtrl.text.trim()),
      descripcion: _descripcionCtrl.text.trim(),
    );

    final ok = await widget.onSave(producto);
    if (!mounted) return;

    if (ok) {
      Navigator.pop(context, true);
    } else {
      setState(() => _saving = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al ${_isEditing ? "actualizar" : "crear"} producto'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Dialog(
      backgroundColor: const Color(0xFF1E1E34),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 460),
        child: Padding(
          padding: const EdgeInsets.all(28),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Title ────────────────────────────────────
                Row(
                  children: [
                    Container(
                      width: 38,
                      height: 38,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(10),
                        color: cs.primary.withAlpha(40),
                      ),
                      child: Icon(
                        _isEditing ? Icons.edit_rounded : Icons.add_rounded,
                        color: cs.primary,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      _isEditing ? 'Editar Producto' : 'Nuevo Producto',
                      style: GoogleFonts.inter(
                        fontSize: 20,
                        fontWeight: FontWeight.w700,
                        color: Colors.white,
                      ),
                    ),
                    const Spacer(),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.close_rounded, size: 20),
                      splashRadius: 18,
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // ── Nombre ──────────────────────────────────
                TextFormField(
                  controller: _nombreCtrl,
                  enabled: !_saving,
                  decoration: const InputDecoration(
                    labelText: 'Nombre *',
                    prefixIcon: Icon(Icons.label_outline_rounded),
                  ),
                  validator: (v) {
                    if (v == null || v.trim().isEmpty) return 'Requerido';
                    if (v.trim().length < 2) return 'Mínimo 2 caracteres';
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // ── Precio & Stock ──────────────────────────
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _precioCtrl,
                        enabled: !_saving,
                        keyboardType: const TextInputType.numberWithOptions(
                          decimal: true,
                        ),
                        inputFormatters: [
                          FilteringTextInputFormatter.allow(
                            RegExp(r'^\d+\.?\d{0,2}'),
                          ),
                        ],
                        decoration: const InputDecoration(
                          labelText: 'Precio *',
                          prefixIcon: Icon(Icons.attach_money_rounded),
                        ),
                        validator: (v) {
                          if (v == null || v.trim().isEmpty) return 'Requerido';
                          final n = double.tryParse(v.trim());
                          if (n == null || n <= 0) return 'Debe ser > 0';
                          return null;
                        },
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: TextFormField(
                        controller: _stockCtrl,
                        enabled: !_saving,
                        keyboardType: TextInputType.number,
                        inputFormatters: [
                          FilteringTextInputFormatter.digitsOnly,
                        ],
                        decoration: const InputDecoration(
                          labelText: 'Stock *',
                          prefixIcon: Icon(Icons.inventory_rounded),
                        ),
                        validator: (v) {
                          if (v == null || v.trim().isEmpty) return 'Requerido';
                          final n = int.tryParse(v.trim());
                          if (n == null || n < 0) return 'Debe ser >= 0';
                          return null;
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // ── Descripción ─────────────────────────────
                TextFormField(
                  controller: _descripcionCtrl,
                  enabled: !_saving,
                  maxLines: 3,
                  decoration: const InputDecoration(
                    labelText: 'Descripción (opcional)',
                    prefixIcon: Padding(
                      padding: EdgeInsets.only(bottom: 40),
                      child: Icon(Icons.description_outlined),
                    ),
                    alignLabelWithHint: true,
                  ),
                ),
                const SizedBox(height: 28),

                // ── Buttons ─────────────────────────────────
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton(
                      onPressed: _saving ? null : () => Navigator.pop(context),
                      child: Text(
                        'Cancelar',
                        style: GoogleFonts.inter(
                          fontWeight: FontWeight.w500,
                          color: Colors.white54,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    SizedBox(
                      width: 130,
                      height: 44,
                      child: ElevatedButton(
                        onPressed: _saving ? null : _submit,
                        style: ElevatedButton.styleFrom(
                          minimumSize: Size.zero,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: _saving
                            ? const SizedBox(
                                width: 22,
                                height: 22,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2.5,
                                  color: Colors.white,
                                ),
                              )
                            : Text(
                                'Guardar',
                                style: GoogleFonts.inter(
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
