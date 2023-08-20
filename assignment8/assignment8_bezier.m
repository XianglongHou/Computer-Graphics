figure; 
t = 0:0.001:1;

%%
h = drawpolyline;
hold on;
hcurve = plot(bezier(h.Position, t), 'g', 'linewidth', 2);
h.addlistener('MovingROI', @(h, evt) bezier(evt.CurrentPosition, t, hcurve));

%%
function po = bezier(p, t, h)
    t = t';
    num = size(p,1)-1;
    po = zeros(size(t,2),2);
    for j = 0:num
       po = po + nchoosek(num, j)*(t.^j).*(1-t).^(num-j)*p(j+1,:); 
    end
    

    po = po*[1;1i];
    if nargin>2,set(h, 'xdata', real(po), 'ydata', imag(po)); end
end

