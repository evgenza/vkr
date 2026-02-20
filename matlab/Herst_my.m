function Herst_my(Y,m,K,d,D,L,R);
Y1=diff(Y);
for k=1:R;
    y=Y(K+(k-1)*d+1:K+(k-1)*d+L);
    dt=fract_dim_f(y); 
    h=Herst_f(y);  H(k)=h; 
    Ii=Inform_f(y); I(k)=Ii;
    Dt=fract_dim_f(y);
    DT(k)=(Dt+2-h+1.21*Ii)/3;  %с поправкой
    Lyap(k)=Lyapunov_f(y,m,D);
end;

hF6=figure; 
set(hF6,'Units','Normalized','Pos',[0.2 0.175 0.78 0.55],...
    'Color',[0.8 0.8 0.8]);
H_sm=exp_smooth_twice(H',0.4);
DT_sm=exp_smooth_twice(DT',0.4);
I_sm=exp_smooth_twice(I',0.4);
Lyap_sm=exp_smooth_twice(Lyap',0.4);

subplot(2,1,1);
plot(H,'LineWidth',4); grid; %axis([0 R 0 2]);
hold on; plot(I,'m','LineWidth',4);
hold on; plot(DT,'g','LineWidth',4);
hold on; plot(DT_sm,'k','LineWidth',4);
hold on; plot(H_sm,'k','LineWidth',4);
hold on; plot(I_sm,'k','LineWidth',4);
legend('Показатель Херста','Эмерджентность','Фрактальная размерность','Сглаживание');
title('Показатель Херста,эмерджентность и фрактальная размерность',...
    'FontSize',14,'FontWeight','Bold');

subplot(2,1,2);
plot(Lyap,'b','LineWidth',4); grid; 
hold on; plot(Lyap_sm,'k','LineWidth',4);
title('Старший показатель Ляпунова','FontSize',14,'FontWeight','Bold');
xlabel('Номер окна','FontSize',14,'FontWeight','Bold'); 