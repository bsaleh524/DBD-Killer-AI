TODO:
* Data
    - change pallet labels to cover everything, not just the portion
    - Make more splits of data augmentations
* Training:
    - use yolo api, not CLI
    - Make the paths make more sense.
    - make a tree split of all stuff(data splits vs yolo models vs epochs vs...)
    - Figure out all important metrics to grab. Focus on those. Make it presentable using some kind of script.

* After decent enough model is made:
    - Pick best model, and figure out how to grab labels, boxes, and scores for deepsort tracking
    - (optional) test on a recorded video
    - How to stream this game from OBS(?) to the model
    - Figure out how to control the game with another computer


to understand:
- what is dfl_loss
- what is cls_loss
- what is box_loss

later on:
- Label huntress dataset and add it. Traps are messing up training.
- start defining agent behavior:
    - STATES (check generators, chase, go hook)
    - ACTIONS (Kick generator, hit survivor, break pallet, etc)
    - TRANSITIONS (pick up survivor, )
    - COST (Distance to generator not worth it, chase_time >threshold-> abandon, etc)


