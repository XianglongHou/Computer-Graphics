nv = size(x, 1);
np=size(P2PVtxIds,1);


y = x;
y(P2PVtxIds,:) = p2pDsts;
f = F+1;

%uniform laplace matrix
% L=sparse(f, f(:, [2 3 1]), 1,nv,nv);
% L = spdiags(-sum(L,2), 0, L);


% cot laplace matrix
adj_matrix = sparse(f, f(:, [2 3 1]), 1,nv,nv);
L=adj_matrix; %adj matrix
for i=1:nv
    a=find(adj_matrix(i,:));
    for j=i+1:length(a)  %i 
        both_adj=intersect(find(adj_matrix(i,:)),find(adj_matrix(a(j),:)));
        weight=0;
        
        for k = 1:length(both_adj)
            v1 = x(i, :) - x(both_adj(k), :);
            v2 = x(a(j), :) - x(both_adj(k), :);
            weight = weight + cot(acos(dot(v1, v2) / (norm(v1) * norm(v2)))) / 2;
        end
        L(i,a(j))=weight;
        L(a(j),i)=weight;
    end
end
diag_L = -sum(L, 2);
L = L + diag(diag_L);




%rhs
rhs=zeros(nv + np ,3);
rhs(1:nv,:) = L * x;
rhs(nv+1:end,:) = p2pDsts;

%penalty method to solve the optimization problem
penalty = 20;

for i=1:np
    L(nv+i,P2PVtxIds(i))=penalty;
    L(nv+i,P2PVtxIds(i))=penalty;
end

rhs(nv+1:end,:) = penalty * p2pDsts;

y = (L'*L)\(L'*rhs);
