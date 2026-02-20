function h=Herst(y);     %Показатель Херста;   y -столбец
z=y-mean(y);  n=length(z); s=std(z);
z1=cumsum(z);
RM=max(z1)-min(z1);
h=(log(RM)-log(s))/log(n);


