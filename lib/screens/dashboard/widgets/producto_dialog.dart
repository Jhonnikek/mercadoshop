import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../core/theme.dart';
import '../../../models/producto.dart';
import '../../../providers/producto_provider.dart';

class ProductoDialog extends StatefulWidget {
  final Producto? producto; // null = create mode

  const ProductoDialog({
    super.key,
    this.producto,
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
      text: widget.producto != null ? widget.producto!.precio.toString() : '',
    );
    _stockCtrl = TextEditingController(
      text: widget.producto != null ? widget.producto!.stock.toString() : '',
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

    final nuevoProducto = Producto(
      id: widget.producto?.id,
      nombre: _nombreCtrl.text.trim(),
      precio: double.parse(_precioCtrl.text.trim()),
      stock: int.parse(_stockCtrl.text.trim()),
      descripcion: _descripcionCtrl.text.trim(),
    );

    try {
      final provider = context.read<ProductoProvider>();
      if (widget.producto == null) {
        await provider.createProducto(nuevoProducto);
      } else {
        await provider.updateProducto(widget.producto!.id!, nuevoProducto);
      }
      if (mounted) Navigator.of(context).pop(true);
    } catch (e) {
      if (!mounted) return;
      setState(() => _saving = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          behavior: SnackBarBehavior.floating,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          backgroundColor: AppTheme.danger.withAlpha(38),
          content: Row(
            children: [
              const Icon(Icons.error_outline_rounded,
                  color: AppTheme.danger, size: 18),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  'Error: $e',
                  style: GoogleFonts.inter(
                      fontSize: 14, color: AppTheme.danger),
                ),
              ),
            ],
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: AppTheme.surface,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 500),
        child: Padding(
          padding: const EdgeInsets.all(28),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Header ──────────────────────────────────
                Row(
                  children: [
                    Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(10),
                        color: AppTheme.primary.withAlpha(38),
                      ),
                      child: Icon(
                        _isEditing
                            ? Icons.edit_rounded
                            : Icons.add_rounded,
                        color: AppTheme.primary,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      _isEditing ? 'Editar Producto' : 'Nuevo Producto',
                      style: GoogleFonts.inter(
                        fontSize: 20,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    const Spacer(),
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.close_rounded,
                          size: 20, color: AppTheme.textSecondary),
                      splashRadius: 18,
                    ),
                  ],
                ),
                const SizedBox(height: 24),

                // ── Nombre ──────────────────────────────────
                _FieldLabel('Nombre'),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _nombreCtrl,
                  enabled: !_saving,
                  style: GoogleFonts.inter(
                      fontSize: 14, color: AppTheme.textPrimary),
                  decoration: const InputDecoration(
                    hintText: 'Nombre del producto',
                    prefixIcon: Icon(Icons.label_outline_rounded, size: 18),
                  ),
                  validator: (v) {
                    if (v == null || v.trim().isEmpty) return 'Requerido';
                    if (v.trim().length < 2) return 'Mínimo 2 caracteres';
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // ── Precio & Stock ───────────────────────────
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _FieldLabel('Precio'),
                          const SizedBox(height: 8),
                          TextFormField(
                            controller: _precioCtrl,
                            enabled: !_saving,
                            keyboardType: const TextInputType.numberWithOptions(
                                decimal: true),
                            inputFormatters: [
                              FilteringTextInputFormatter.allow(
                                  RegExp(r'^\d+\.?\d{0,2}')),
                            ],
                            style: GoogleFonts.inter(
                                fontSize: 14, color: AppTheme.textPrimary),
                            decoration: const InputDecoration(
                              hintText: '0.00',
                              prefixIcon: Icon(Icons.attach_money_rounded,
                                  size: 18),
                            ),
                            validator: (v) {
                              if (v == null || v.trim().isEmpty) {
                                return 'Requerido';
                              }
                              final n = double.tryParse(v.trim());
                              if (n == null || n <= 0) return 'Debe ser > 0';
                              return null;
                            },
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _FieldLabel('Stock'),
                          const SizedBox(height: 8),
                          TextFormField(
                            controller: _stockCtrl,
                            enabled: !_saving,
                            keyboardType: TextInputType.number,
                            inputFormatters: [
                              FilteringTextInputFormatter.digitsOnly,
                            ],
                            style: GoogleFonts.inter(
                                fontSize: 14, color: AppTheme.textPrimary),
                            decoration: const InputDecoration(
                              hintText: '0',
                              prefixIcon:
                                  Icon(Icons.inventory_rounded, size: 18),
                            ),
                            validator: (v) {
                              if (v == null || v.trim().isEmpty) {
                                return 'Requerido';
                              }
                              final n = int.tryParse(v.trim());
                              if (n == null || n < 0) return 'Debe ser >= 0';
                              return null;
                            },
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // ── Descripción ──────────────────────────────
                _FieldLabel('Descripción (opcional)'),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _descripcionCtrl,
                  enabled: !_saving,
                  maxLines: 3,
                  style: GoogleFonts.inter(
                      fontSize: 14, color: AppTheme.textPrimary),
                  decoration: const InputDecoration(
                    hintText: 'Descripción breve del producto...',
                    prefixIcon: Padding(
                      padding: EdgeInsets.only(bottom: 40),
                      child: Icon(Icons.description_outlined, size: 18),
                    ),
                    alignLabelWithHint: true,
                  ),
                ),
                const SizedBox(height: 28),

                // ── Actions ──────────────────────────────────
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    // Ghost cancel button
                    OutlinedButton(
                      onPressed: _saving ? null : () => Navigator.pop(context),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppTheme.textSecondary,
                        side: const BorderSide(color: AppTheme.border),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 20, vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      child: Text(
                        'Cancelar',
                        style: GoogleFonts.inter(
                            fontSize: 14, fontWeight: FontWeight.w500),
                      ),
                    ),
                    const SizedBox(width: 12),
                    // Primary save button
                    SizedBox(
                      height: 44,
                      width: 130,
                      child: ElevatedButton(
                        onPressed: _saving ? null : _submit,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.primary,
                          foregroundColor: AppTheme.textPrimary,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                          elevation: 0,
                        ),
                        child: _saving
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2.5,
                                  color: AppTheme.textPrimary,
                                ),
                              )
                            : Text(
                                'Guardar',
                                style: GoogleFonts.inter(
                                  fontSize: 14,
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

// ── Shared label widget ─────────────────────────────────────
class _FieldLabel extends StatelessWidget {
  final String text;
  const _FieldLabel(this.text);

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: GoogleFonts.inter(
        fontSize: 13,
        fontWeight: FontWeight.w500,
        color: AppTheme.textSecondary,
      ),
    );
  }
}
