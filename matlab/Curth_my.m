function Curth_my(Y,K,d,L,R);
Y1=diff(Y);
for k=1:R;
    y=Y(K+(k-1)*d+1:K+(k-1)*d+L);
    sig2=cov(y);  y0=y-mean(y);
    Curth(k)=mean(y0.^4)/(sig2^2);
    V(k)=max(y0)/std(y0);
end;

hF6=figure; 
set(hF6,'Units','Normalized','Pos',[0.2 0.175 0.78 0.55],...
    'Color',[0.8 0.8 0.8]);
%Curth_sm=exp_smooth_twice(Curth',0.5);

subplot(2,1,1);
plot(Curth,'LineWidth',4); grid; hold on; 
title('Фактор куртозиса (динамика эксцесса)','FontSize',14,'FontWeight','Bold');
subplot(2,1,2);
plot(V,'k','LineWidth',4); grid; hold on; 
title('Динамика пик-фактора','FontSize',14,'FontSize',14,'FontWeight','Bold');
ylabel('Пик-фактор','LineWidth',14,'FontSize',14,'FontWeight','Bold');
xlabel('Время (с)','FontSize',14,'FontSize',14,'FontWeight','Bold'); 