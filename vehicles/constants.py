SIPP_CATEGORY_CHOICES = [
    ('M', 'Mini'), ('E', 'Ekonomi'), ('C', 'Kompakt'), ('I', 'Orta'),
    ('S', 'Standart'), ('F', 'Tam Boyut'), ('P', 'Premium'), ('L', 'Lüks'), ('X', 'Özel'),
]

# X (Özel) sıralamaya dahil değil — sadece kendisiyle eşleşir, otomatik yükseltilmez.
SIPP_CATEGORY_RANK = {'M': 0, 'E': 1, 'C': 2, 'I': 3, 'S': 4, 'F': 5, 'P': 6, 'L': 7}

SIPP_BODY_TYPE_CHOICES = [
    ('B', '2 Kapılı'), ('C', '2/4 Kapılı'), ('D', '4 Kapılı'),
    ('W', 'Wagon'), ('V', 'Minivan'), ('S', 'SUV'), ('T', 'Kamyonet'),
]
