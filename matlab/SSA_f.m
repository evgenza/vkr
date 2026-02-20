function s0=SSA_f(y);     %y - столбец, s - столбец высотой l
n=length(y);
y_sm=exp_smooth_twice(y,0.1);
yd=y-y_sm;
[yh,yl]=envelope(yd);  %огибающая
l=12;                  %количество сингулярных чисел
for j=1:l-1;
    X(:,j)=yh(j:n-l+j);
    %X(:,j)=yl(j:n-l+j);  %всё равно, какую брать
end;
[L,S,R]=svd(X,0);
s=diag(S);  %столбец сингулярных чисел
ss=-diff(log(s));
s0=min(ss);

