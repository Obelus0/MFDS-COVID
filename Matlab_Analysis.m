
%% read data
clc
clear
close all
ds = datastore('Dataset_Question3');

ds.Files % check if the order matches as below
% 1-Dataset_Question3\AgeGroupDetails.csv            
% 2-Dataset_Question3\HospitalBedsIndia.csv          
% 3-Dataset_Question3\ICMRTestingDetails.csv         
% 4-Dataset_Question3\IndividualDetails.csv          
% 5-Dataset_Question3\covid_19_india.csv             
% 6-Dataset_Question3\population_india_census2011.csv

data = cell(1,length(ds.Files));
for i = 1:length(ds.Files)
    data{i} = readtable(ds.Files{i});
end

%{
%% Q1 Which age group is the most infected?
% ans : 20-29
% plot graph
data{1}.AgeGroup = categorical(data{1}.AgeGroup);
bar(data{1}.AgeGroup,data{1}.TotalCases)
xlabel('Age group')
ylabel('TotalCases')

%% Q2 Plot graphs of the cases observed, recovered, 
% deaths per day country-wise and statewise.

data{5}.State_UnionTerritory = categorical(data{5}.State_UnionTerritory);
data{5}.Date = datetime(data{5}.Date);
data{5}.DateCat = categorical(data{5}.Date);

% method 1
figure('Name','cumulative Confirmed')
gscatter(data{5}.Date,data{5}.Confirmed,...
    data{5}.State_UnionTerritory);


figure('Name','cumulative Cured')
gscatter(data{5}.Date,data{5}.Cured,...
    data{5}.State_UnionTerritory)

figure('Name','cumulative Deaths')
gscatter(data{5}.Date,data{5}.Deaths,...
    data{5}.State_UnionTerritory)

% method 2
states = unique(data{5}.State_UnionTerritory);

figure('Name','cumulative Confirmed')
for i = 1:4
    leg = [];
    for j = 8*(i-1)+1:8*i
        t = data{5}(data{5}.State_UnionTerritory==states(j),:);
        subplot(2,2,i)
        plot(t.Date,t.Confirmed,'linewidth',2)
        grid on
        hold on        
        leg = [leg,{char(states(j))}];
    end
    legend(leg,'location','northwest')
end
suptitle('cumulative Confirmed (statewise)')

figure('Name','cumulative Cured')
for i = 1:4
    leg = [];
    for j = 8*(i-1)+1:8*i
        t = data{5}(data{5}.State_UnionTerritory==states(j),:);
        subplot(2,2,i)
        plot(t.Date,t.Cured,'linewidth',2)
        grid on
        hold on        
        leg = [leg,{char(states(j))}];
    end
    legend(leg,'location','northwest')
end
suptitle('cumulative Cured (statewise)')

figure('Name','cumulative Deaths')
for i = 1:4
    leg = [];
    for j = 8*(i-1)+1:8*i
        t = data{5}(data{5}.State_UnionTerritory==states(j),:);
        subplot(2,2,i)
        plot(t.Date,t.Deaths,'linewidth',2)
        grid on
        hold on        
        leg = [leg,{char(states(j))}];
    end
    legend(leg,'location','northwest')
end
suptitle('cumulative Deaths (statewise)')

%}
%% Q6 

clc
t = [];
% 4-Dataset_Question3\IndividualDetails.csv  
t = data{4};
t.detected_state = categorical(t.detected_state);

% statewise cases
figure('Name','Statewise cases')
title('Statewise cases')
h1 = histogram(t.detected_state);
StateCounts = table(h1.Categories',h1.Values');
StateCounts.Properties.VariableNames = {'State','Counts'};
StateCountsSorted = sortrows(StateCounts,2,'descend');
disp(StateCountsSorted)

% filter based on top 5 states
Top_5_States = categorical(StateCountsSorted.State(1:5));

t_filt = [];
for i = 1:5
   t_filt = [t_filt; t(t.detected_state==Top_5_States(i),:)] ;
end


word_1 =  cell(1,1);

% get 1st words in notes
for i = 1:height(t)
    notes = split(t.notes{i},' ');
    word_1{i} = notes{1};    
end
uniqueWords_1 = sort(unique(word_1)); % classify based on this

% set as Delhi to secondary
for i = 1:height(t)
    notes = split(t.notes{i},' ');
    for j = 1:length(notes)        
        if(strcmp(notes{j},'Delhi'))
            t.notes{i} = 'Secondary';
        end
    end
end

% set as primary, secondary, tertiary
% check IDs again in <uniqueWords_1>
% id1, id2, id3 for all states
% segregate for <t_filt>
id1 = [3,104,109,110,122,36,37,43,52,61,90,108,];
id2 = [2,4:29,31:35,38:42,44,45,46,48:51,53:60,62:89,91:103,105:107,111:121];
id3 = [1,30,47];

for i = 1:height(t)
    notes = split(t.notes{i},' ');
    for j = 1:length(notes)        
        if(any((strcmp(notes{j},uniqueWords_1(id1)))))
            t.notes{i} = 'Primary';
        elseif(any((strcmp(notes{j},uniqueWords_1(id2)))))
            t.notes{i} = 'Secondary';
        elseif(any((strcmp(notes{j},uniqueWords_1(id3)))))
            t.notes{i} = 'Tertiary';
        
        end
    end
end

t.notes = categorical(t.notes);
% check if anything left off
unique(t.notes)

% counts
figure('Name','Classified #cases')
h = histogram(t.notes);
Catcounts = table(h.Categories',h.Values');
Catcounts.Properties.VariableNames = {'Category','Values'}


%% Q8

clc
% data{5} preprocessing done in Q2
% comment 3 lines below if you ran them, else run now
data{5}.State_UnionTerritory = categorical(data{5}.State_UnionTerritory);
data{5}.Date = datetime(data{5}.Date);
data{5}.DateCat = categorical(data{5}.Date);

t = data{5};
G = findgroups(t.DateCat);
% find sum of all states values of conf, cure, deaths
ConfTotal = splitapply(@sum,t.Confirmed,G);
CureTotal = splitapply(@sum,t.Cured,G);
DeathTotal = splitapply(@sum,t.Deaths,G);

% plot cumulative cases and cases/day  for India
% (sum of all states)
% give your comments

figure('Name','India Covid-19')
title('India Covid-19')
subplot 231
plot(unique(t.Date),ConfTotal,'b','linewidth',2)
grid on
title('Confirmed (cumulative)')
subplot 232
plot(unique(t.Date),CureTotal,'g','linewidth',2)
grid on
title('Cured (cumulative)')
subplot 233
plot(unique(t.Date),DeathTotal,'r','linewidth',2)
grid on
title('Deaths (cumulative)')

diffDates = unique(t.Date);
diffDates = diffDates(2:end);
subplot 234
plot(diffDates,diff(ConfTotal),'b','linewidth',2)
grid on
title('Confirmed (cases/day)')
subplot 235
plot(diffDates,diff(CureTotal),'g','linewidth',2)
grid on
title('Cured (cases/day)')
subplot 236
plot(diffDates,diff(DeathTotal),'r','linewidth',2)
grid on
title('Deaths (cases/day)')