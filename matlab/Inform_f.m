function I=Inform(y);     %Информационный показатель, y -столбец
n=length(y);   x0=1:n;
step=0.1;  x=0:step:n;  
ys=spline(x0,y',x');
H=hist(ys,length(x));  
H=H/sum(H);
J=find(H);   H1=log(H(J));
I=-sum(H(J).*H1)*step;


