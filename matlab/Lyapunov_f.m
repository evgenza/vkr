function g=Lyapunov_f(y,m,D);   %Оценивание показателя Ляпунова
%по отрезку ряда y для D контрольных шагов с m зонами разбиения
%clear; clc;                  %показатель хаотичности по Ляпунову           
%load('Data','YY');  [N,m]=size(YY);   % <288000x6>     6 каналов
%L=200;  r=5;  y=YY(1:L,r);      %берём канал номер r
%m=30;   D=4;
    L=length(y);
    eps=(max(y)-min(y))/m;          % высота ячейки разбиения

    nn=1:3:round(L/2);
for n=1:3:round(L/2);
    y0=y(n); I=find(abs(y-y0)<eps);  P=length(I);
    v=ones(1,length(nn)); T=ones(1,length(nn));
    for k=1:P-1;
       z1=y(I(k):L-(I(k+1)-I(k)));  z2=y(I(k+1):L);   z=abs(z1-z2);
       JJ=find(z>D*eps);       J=min(min(JJ));
       u1=abs(z1(1)-z2(1)+1);  u2=abs(z1(J)-z2(J)+1);
          if (u1~=0)&(u2~=0);  
             v(k)=log(u2+10)-log(u1+10);    T(k)=J;
          else v(k)=0;  T(k)=0;
          end;        
   end;
   V(n)=sum(v);   TT(n)=sum(T);
end;
g=sum(V)/sum(TT);
    