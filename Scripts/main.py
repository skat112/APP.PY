import math



print('введите коэфициенты квадратного уравнения')

print('ax^2 + bx + c = 0:')

a = float(input('введите коэфициент a= '))

b = float(input('введите коэфициент b= '))

c = float(input('введите коэфициент c= '))



discr = b**2 - 4 * a * c

print('Дискриминант D = %.2f' % discr)

if a == 0:

    x = -c / b

    print(x)

elif discr > 0:

    x1 = (-b + discr ** 0.5) / (2 * a)

    x2 = (-b - discr ** 0.5) / (2 * a)

    print('x1 = %.2f \nx2 = %.2f' % (x1, x2))

elif discr == 0:

    x = -b / (2 * a)

    print('x = %.2f' % x)

else:

    print('Корней нет ')