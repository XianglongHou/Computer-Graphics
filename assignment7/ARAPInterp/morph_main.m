[x,t] = readObj('elephant_s');
y = readObj('elephant_t');


figure('position', [10 40 1210, 840]); subplot(131); drawmesh(t, x);
subplot(133); drawmesh(t, y);
subplot(132); h=drawmesh(t, x);

%% 构建系数矩阵


for w = 0:0.01:1
    %% placeholder: linear interpolating the vertex positions
    
    %% TODO: finish the ARAP interpolation function
    z = ARAP_interp(x, y, t, w);
    %% draw the result
    set(h,'vertices',z);
    drawnow; pause(0.01);
end



function h = drawmesh(t, x)
    h = trimesh(t, x(:,1), x(:,2), x(:,1), 'facecolor', 'interp', 'edgecolor', 'k');
    axis equal; axis off; view(2);
end



function z = ARAP_interp(x, y, t, w)
% x: 初始点 (N*3)
% t: 邻接索引 (M*3)
% y: 最终点 (N*3)
% w: 时间

% 获取面的数量
nt = size(t, 1);
%2D
x = x(:,1:2);
y = y(:,1:2);

% 构建稀疏矩阵L
a = 1:nt;
a1 = [2*a - 1, 2*a, 2*a - 1, 2*a, 2*nt + 1];
t1 = [t(a, 3)', t(a, 2)', t(a, 1)', t(a, 1)', 1];
value = [ones(1, 2*nt), -ones(1, 2*nt), 1];
L = sparse(a1, t1, value);

% 初始化变量
b = zeros(2*nt + 1, 2);
b1 = zeros(nt, 2);
b2 = zeros(nt, 2);

% 计算每个面对应的矩阵At和b向量
X_vec1 = x(t(:, 3), :) - x(t(:, 1), :);  % vec1->3
X_vec2 = x(t(:, 2), :) - x(t(:, 1), :);  
Y_vec1 = y(t(:, 3), :) - y(t(:, 1), :);  
Y_vec2 = y(t(:, 2), :) - y(t(:, 1), :);  
for i = 1:nt
    % 计算左边的矩阵L
    l_mat = [X_vec1(i, :)', X_vec2(i, :)'];
    
    % 计算右边的矩阵R
    r_mat = [Y_vec1(i, :)', Y_vec2(i, :)'];
    
    % 计算旋转和缩放
    ans_A = r_mat / l_mat;
    [Ra, D, Rb] = svd(ans_A);
    Rb = Rb';
    Rr = Ra * Rb;
    theta = w * atan2(Rr(1, 2), Rr(1, 1));
    Rtr = [cos(theta), sin(theta); -sin(theta), cos(theta)];
    S = Rb' * D * Rb;
    At = Rtr * ((1 - w) * eye(size(S, 1)) + w * S);
    
    % 计算权重并构建b向量
    w1 = norm(X_vec1(i, :)) / norm(Y_vec1(i, :));
    b1(i, :) = (At * l_mat(:, 1))' * w1;
    b2(i, :) = (At * l_mat(:, 2))' * w1;

    
end

% 设置最后一行的边界条件

b(end, :) = x(1, :);
b(1:2:2*nt - 1, :) = b1;
b(2:2:2*nt, :) = b2;

% 最小二乘求解线性方程组
z = zeros(size(x, 1), 3);
z(:, 1:2) = (L' * L) \ (L' * b);


end