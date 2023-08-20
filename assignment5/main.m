[v, f, ~, ~] = readObj('cathead.obj');
[B, ~] = findBoundary(v, f);

%确定边界点

n = length(B);
boundary_angles = linspace(0, 2 * pi, n + 1);
boundary_angles = boundary_angles(1:end-1);
boundary_coords = [cos(boundary_angles); sin(boundary_angles)];

% 构建系数矩阵

L = zeros(size(v, 1));
for i = 1:size(f, 1)
    for j = 1:3
        v1 = f(i, j);
        v2 = f(i, mod(j, 3) + 1);
        L(v1, v2) = L(v1, v2) + 1;
        L(v2, v1) = L(v2, v1) + 1;
    end
end

for i = 1:size(v, 1)
    L(i, i) = -sum(L(i, :));
end

%modify boundary

for i = 1:n
    L(B(i), :) = 0;
    L(B(i), B(i)) = 1;
end

%右端项
b = zeros(size(v, 1), 2);

for i = 1:n
    b(B(i), :) = boundary_coords(:, i)';
end

param_coords = L \ b;
drawmesh(f, param_coords,B)
