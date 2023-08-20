function imret = blendImagePoisson(im1, im2, roi, targetPosition)

% input: im1 (background), im2 (foreground), 
% 
% roi (in im2), targetPosition ( in im1)

%% TODO: compute blended image

% scaling utf8 to double [0,1]
im1 = im2double(im1);
im2 = im2double(im2);
imret=im1;
[w1,h1,~]=size(im1);
[w2,h2,~] = size(im2);

roi = fliplr(roi);
targetPosition = fliplr(targetPosition);

% Extract the region of interest (roi) from im2,im1
[xpix1, ypix1] = meshgrid(1:w1, 1:h1);
[xpix2,ypix2]=meshgrid(1:w2,1:h2);

roi_points2 = inpolygon(xpix2,ypix2,roi(:,1),roi(:,2))';
roi_points1 = inpolygon(xpix1,ypix1,targetPosition(:,1),targetPosition(:,2))';
roiIm2 = im2 .* repmat(roi_points2, [1, 1, size(im2,3)]);
roiIm1 = im1 .* repmat(roi_points1, [1, 1, size(im1,3)]);

[roi_im1_x,roi_im1_y] = find(roi_points1);
[roi_im2_x,roi_im2_y] = find(roi_points2);

% divide roi into  inner points and outer points(boundary points)
inner_points1 = roi_points1 &  circshift(roi_points1, [0 1]) & circshift(roi_points1, [0 -1]) & circshift(roi_points1, [1 0]) & circshift(roi_points1, [-1 0]);
outer_points1 = roi_points1 - inner_points1;
inner_points2 = roi_points2 &  circshift(roi_points2, [0 1]) & circshift(roi_points2, [0 -1]) & circshift(roi_points2, [1 0]) & circshift(roi_points2, [-1 0]);
outer_points2 = roi_points2 - inner_points2;



% Compute the Laplacian of image within the target region
kernel = [0 1 0; 1 -4 1; 0 1 0];
laplacianIm2  = imfilter(roiIm2, kernel);


% conduct Possion equations
[inner_x, inner_y] = find(inner_points2);
[outer_x, outer_y] = find(outer_points2);
[outer_x1,outer_y1] = find(outer_points1);


% get the number of inner points and boundary points
N = length(inner_x);
M = length(outer_x);

% find the linear index of inner points'neighbors
mid_x = inner_x;
mid_y = inner_y;


[~,loc_mid]=ismember([mid_x,mid_y],[roi_im2_x,roi_im2_y], 'rows');

loc_mid=loc_mid';
[~,loc_left]=ismember([mid_x-1,mid_y],[roi_im2_x,roi_im2_y], 'rows');
loc_left = loc_left';
[~,loc_right]=ismember([mid_x+1,mid_y],[roi_im2_x,roi_im2_y], 'rows');
loc_right = loc_right';
[~,loc_up]=ismember([mid_x,mid_y-1],[roi_im2_x,roi_im2_y], 'rows');
loc_up=loc_up';
[~,loc_down]=ismember([mid_x,mid_y+1],[roi_im2_x,roi_im2_y], 'rows');
loc_down = loc_down';
[~,loc_out]=ismember([outer_x,outer_y],[roi_im2_x,roi_im2_y], 'rows');
loc_out = loc_out';


% Generate coefficient matrix and make it sparse

A=eye(M+N,M+N);
b = zeros(N+M, size(im1, 3));

A(sub2ind(size(A), loc_mid , loc_left))=1 ;
A(sub2ind(size(A), loc_mid , loc_right))=1 ;
A(sub2ind(size(A), loc_mid , loc_up))=1 ;
A(sub2ind(size(A), loc_mid, loc_down))=1 ;
A(sub2ind(size(A), loc_mid , loc_mid)) = -4 ;


S = sparse(A);
sol=zeros(M+N,3);

%generate the right handside vector and solve equations

%这段是可以向量化的但是循环次数少就懒得写了
for k=1:3
    b(loc_mid,k) = laplacianIm2(sub2ind(size(laplacianIm2),inner_x,inner_y,k*ones(N,1)));
    b(loc_out,k) = roiIm1(sub2ind(size(roiIm1),outer_x1,outer_y1,k*ones(M,1)));
    sol(:,k)= S\b(:,k);
    imret(sub2ind(size(imret),roi_im1_x,roi_im1_y,k*ones(M+N,1))) = sol(:,k);
end

%back to unit8
%bonus
%计算A的QR分解(因为A是稀疏矩阵，代价很高）
% [Q,R] = qr(A);
% 
% for k=1:3
%     bt=Q'*b(:,k);
%     sol(:,k) = R\bt;
%     imret(sub2ind(size(imret),roi_im1_x,roi_im1_y,k*ones(M+N,1))) = sol(:,k);
% end

%back to unit8
imret = uint8(imret * 255);
end
