load('res.mat');

res=cell2mat(res);
otherT = cell2table(other);

confs = unique(other(:,1)); 
vars = unique(other(:,2));

%% todas las configuraciones juntas
figure
title('Todas las configuraciones')
xlabel('Tiempo')
ylabel('Concentracion')
hold on

for i = 1:length(confs)
    ids=find(strcmp(other(:,1),confs{i}));
    
    plot(res(ids,8),res(ids,9))

end
legend(confs)
hold off


%% todas las configuraciones agrupadas por variable estudiada


T = cell2table(other);
unk = unique(T, 'rows');
unk = table2cell(unk);

for i = 1:length(vars)
    rows = find(strcmp(unk(:,2),vars{i}));
    corresponding_confs = unk(rows,1);
    
    figure
    
    title(vars{i})
    xlabel('Tiempo')
    ylabel('Concentracion')
    hold on
    for j = 1:length(rows)
        ids=find(strcmp(other(:,1),corresponding_confs{j}));
        
        plot(res(ids,8),res(ids,9))
    end
    legend(corresponding_confs)
    hold off
end