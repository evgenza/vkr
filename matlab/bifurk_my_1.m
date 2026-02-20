function bifurk_my_1(DT,H,G,L0,L1);
%Кумулятивные суммы
hF8=figure; 
set(hF8,'Units','Normalized','Pos',[0.2 0.175 0.78 0.6],...
    'Color',[0.8 0.8 0.8]);    
    DT0=mean(DT(1:L0));   DT1=DT-DT0;   sDT=std(DT);
    H0=mean(H(1:L0));     H1=H-H0;      sH=std(H);
    G0=mean(G(1:L0));     G1=G-G0;      sG=std(G);

subplot(1,3,1);  
   plot(cumsum(DT1),'LineWidth',2,'LineWidth',4); grid;
   hold on; plot([1 L0+L1],20*[sH sH],'k','LineWidth',4);
   hold on; plot([1 L0+L1],-20*[sH sH],'k','LineWidth',4);
title('Кумулятивные суммы','FontSize',12,'FontWeight','Bold');
ylabel('Фрактальная размерность','FontSize',12,'FontWeight','Bold'); 
xlabel('Окно перед скачком','FontSize',12,'FontWeight','Bold'); 

subplot(1,3,2);  
   plot(cumsum(H1),'LineWidth',5); grid;
   hold on; plot([1 L0+L1],200*[sDT sDT],'k','LineWidth',5);
   hold on; plot([1 L0+L1],-200*[sDT sDT],'k','LineWidth',5);
   title('Кумулятивные суммы','FontSize',12,'FontWeight','Bold');
ylabel('Показатель Гёльдера','FontSize',12,'FontWeight','Bold'); 
xlabel('Окно перед скачком','FontSize',12,'FontWeight','Bold');

subplot(1,3,3);  
   plot(cumsum(G1),'LineWidth',5); grid;
   hold on; plot([1 L0+L1],25*[sG sG],'k','LineWidth',5);
   hold on; plot([1 L0+L1],-25*[sG sG],'k','LineWidth',5);
title('Кумулятивные суммы','FontSize',12,'FontWeight','Bold');
ylabel('Показатель Ляпунова','FontSize',12,'FontWeight','Bold'); 
xlabel('Окно перед скачком','FontSize',12,'FontWeight','Bold');


