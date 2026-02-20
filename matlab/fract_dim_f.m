function Dt=fract_dim_f(y);   %оценивание фрактальной размерности столбца y <Lx1>
    L=length(y);  
    eps=0.05;
 
for n=1:L;
    y0=y(n); I=find(abs(y-y0)<eps);  P=length(I)/L/2;
    DT(n)=log(P)/log(eps);    
end;
Dt=mean(DT);
