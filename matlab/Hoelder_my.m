function Hoelder_my(Y,m,K,d,D,L,R);
for k=1:R;
    y=Y(K+(k-1)*d+1:K+(k-1)*d+L);
    g(k)=Hoelder_f(y); 
    dd(k)=max(y)-min(y);
end;

hF8=figure; 
set(hF8,'Units','Normalized','Pos',[0.2 0.175 0.78 0.55],...
    'Color',[0.8 0.8 0.8]);
g_sm=exp_smooth_twice(abs(g'),0.2);

%subplot(2,1,1);
plot(abs(g),'LineWidth',3); grid; %axis([0 R 0 1]);
hold on; plot(g_sm,'k','LineWidth',4);
title('Показатель Гёльдера','FontSize',14,'FontWeight','Bold');

%subplot(2,1,2);
%plot(dd,'LineWidth',3); grid;
%title('Размах на скользящем окне','FontSize',14,'FontWeight','Bold');
%xlabel('Номер окна','FontSize',12); 