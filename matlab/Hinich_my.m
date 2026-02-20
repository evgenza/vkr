function Hinich_my(Y,K,d,L,R);
%Тест Хинича на заданной системе скользящих окон 
Y1=diff(Y,2);  
for k=1:R;
      X=Y1(K+d*(k-1)+1:K+d*(k-1)+L,:);     
      [sg, sl]=GLSTAT(X,0.51,128);
      
      P_gauss(k)=sg(3);   del_R(k)=abs(sl(1)-sl(3));  
  end;
  hF3=figure; 
  set(hF3,'Units','Normalized','Pos',[0.2 0.175 0.78 0.55],...
    'Color',[0.8 0.8 0.8]);
  subplot(2,1,1);  bar(P_gauss,'LineWidth',2); grid;
title('Тест Хинича','FontSize', 15,'FontWeight','bold');
ylabel('P_gauss','FontSize', 14, 'FontWeight', 'bold');
axis([0 R 0 1.1]);
  subplot(2,1,2);  bar(del_R,'LineWidth',2); grid;
axis([0 R 0 5]);
ylabel('del_R','FontSize', 14, 'FontWeight', 'bold');
xlabel('Номер скользящего окна','FontSize',14,'FontWeight','bold');
  