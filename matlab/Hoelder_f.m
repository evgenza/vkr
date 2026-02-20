function g=Hoelder_f(y);   %Оценивание показателя Гёльдера
%по сплайн-аппроксимации ряда y <Lx1>
n=length(y); 
for k=1:n-1;
    y0=y(k);
    for j=1:n-k;
    del_x=j; del_y=abs(y(k+j)-y0);
    alp(j)=log(del_y)/log(del_x);        
    end;
    ALP(k)=max(alp);
end;
g=min(ALP);
        

