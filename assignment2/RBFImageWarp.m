function im2 = RBFImageWarp(im, psrc, pdst)

% input: im, psrc, pdst
% 使用说明：目前是没有去除黑点的情形
% 去除黑点有两个方法：1.注释33行，取消36，37行的注释
% 2.注释33行，取消37行的注释 （在选点时需要先选目标点再选初始点才可达到目标效果）
%% calculate coe A(a_i)
d=1000;

psrc=fliplr(psrc);
pdst=fliplr(pdst);
%cal matrix b_i(p_j)
B = 1./((psrc(:,1)-psrc(:,1)').^2 + (psrc(:,2)-psrc(:,2)').^2 +d);
A = B\(pdst-psrc);

%% basic image manipulations
% get image (matrix) size
[h, w, dim] = size(im);
%im2 = im;
im2 = zeros(h,w,dim,'uint8');

%% use loop to negate image
%% TODO: compute warpped image
for i=1:h
    for j=1:w
            
        bx = 1./(sum(([i j]-psrc).^2,2)+d); %calculate b_i(x)
        new_index=round(bx'*A)+[i j];
        
        %check boundary
        if all(new_index>0) && new_index(1)<=h && new_index(2)<=w
            %这个方法是有黑点的
              im2(new_index(1),new_index(2),:)=im(i,j,:);  

             %这个方法是没有黑点的 bonus
%              new_index=-round(bx'*A)+[i j]; 
%             im2(i,j,:)=im(new_index(1),new_index(2),:);

        end
    end
end


