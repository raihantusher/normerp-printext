def __getattr__(name):
    # Lazy import individual serializer files when needed
    if name == 'CustomerSerializer':
        from .customer_srializer import CustomerSerializer
        return CustomerSerializer
    elif name == 'AssetSerializer':
        from .Accounting_serializer import AssetSerializer
        return AssetSerializer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")