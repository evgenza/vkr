function [DT,H,G]=bifurk_my(Y,m,D,L0,L1,J,k);  
%Выводы участков перед k-м скачком на фазовые плоскости
u=J(k);                         %координата выбранного скачка

for j=1:L0+L1;
    YY=Y(u-L0-L1+j:u-L0+j-1);
    h(j)=Herst_f(YY);
    I(j)=Inform_f(YY);
    Dt(j)=fract_dim_f(YY);  DT(j)=(Dt(j)+4-h(j)+1.21*I(j))/3;  %с поправкой    
    H(j)=Hoelder_f(YY);
    G(j)=Lyapunov_f(YY,m,D);
end;
    DT0=mean(DT(1:L0));   DT1=DT-DT0;
    H0=mean(H(1:L0));     H1=H-H0;
    G0=mean(G(1:L0));     G1=G-G0;
alp=0.1;
DT_sm=exp_smooth_twice(DT',alp);
H_sm=exp_smooth_twice(H',alp);
G_sm=exp_smooth_twice(G',alp);
    sDT=std(DT(L1-L0+1:L1));
    sH=std(H(L1-L0+1:L1));
    sG=std(G(L1-L0+1:L1));

hF7=figure; 
set(hF7,'Units','Normalized','Pos',[0.2 0.175 0.78 0.6],...
    'Color',[0.8 0.8 0.8]);    
subplot(1,2,1);    
plot(H(1:L0),DT(1:L0),'*b','LineWidth',5); grid; %axis([0 1 0 2]);
hold on; plot(H(L0+1:L0+L1),DT(L0+1:L0+L1),'*r','LineWidth',5);
xlabel('Показатель Гёльдера','FontSize',12,'FontWeight','Bold'); 
ylabel('Фрактальная размерность','FontSize',12,'FontWeight','Bold'); 
title('Последние участки перед n-м скачком','FontSize',12,'FontWeight','Bold');
subplot(1,2,2);
plot(H(1:L0),G(1:L0),'*b','LineWidth',5); grid; %axis([0 1 0 2]);
hold on; plot(H(L0+1:L0+L1),G(L0+1:L0+L1),'*r','LineWidth',5);
xlabel('Показатель Гёльдера','FontSize',12,'FontWeight','Bold'); 
ylabel('Старший показатель Ляпунова','FontSize',12,'FontWeight','Bold'); 
title('Последние участки перед n-м скачком','FontSize',12,'FontWeight','Bold');







