import React, {Children, cloneElement} from 'react';
import PropTypes from 'prop-types';
import {cn} from '@/lib/utils';

export const ButtonGroup = ({
                                className,
                                orientation = 'horizontal',
                                children,
                            }) => {
    const totalButtons = Children.count(children);
    const isHorizontal = orientation === 'horizontal';
    const isVertical = orientation === 'vertical';

    return (
        <div
            className={cn(
                'flex',
                {
                    'flex-col': isVertical,
                    'w-fit': isVertical,
                },
                className
            )}
        >
            {Children.map(children, (child, index) => {
                const isFirst = index === 0;
                const isLast = index === totalButtons - 1;

                return cloneElement(child, {
                    className: cn(
                        {
                            'rounded-l-none': isHorizontal && !isFirst,
                            'rounded-r-none': isHorizontal && !isLast,
                            'border-l-0': isHorizontal && !isFirst,

                            'rounded-t-none': isVertical && !isFirst,
                            'rounded-b-none': isVertical && !isLast,
                            'border-t-0': isVertical && !isFirst,
                        },
                        child.props.className
                    ),
                });
            })}
        </div>
    );
};

// Optional: Add PropTypes for better runtime checks
ButtonGroup.propTypes = {
    className: PropTypes.string,
    orientation: PropTypes.oneOf(['horizontal', 'vertical']),
    children: PropTypes.node.isRequired,
};
