def calc(sub, disc=0, svc=0.10, vat=0.07):
    base = max(sub - disc, 0); s = round(base * svc, 2); v = round((base + s) * vat, 2)
    return dict(subtotal=sub, discount=disc, service=s, vat=v, total=round(base + s + v, 2))
def split(total, people):  # แยกบิลเท่าๆ กัน
    return round(total / max(people, 1), 2)
